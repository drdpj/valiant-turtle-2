#************************************************************************ 
#
#   pulse_generator.py
#
#   Stepper motor control (via DRV8825)
#   Valiant Turtle 2 - Robot firmware
#   Copyright (C) 2024 Simon Inns
#
#   This file is part of Valiant Turtle 2
#
#   This is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   Email: simon.inns@gmail.com
#
#************************************************************************

import library.logging as logging
from machine import Pin
import rp2

# This assists if there is an error during an ISR
import micropython
micropython.alloc_emergency_exception_buf(100)

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def pulse_generator():
    wrap_target()
    pull(block)             # Pull (with blocking) FIFO into OSR (first, number of steps)
    mov(x, osr)             # Store the OSR in X

    pull(block)             # Pull (with blocking) FIFO into OSR (second, number of delay cycles)
    mov(y, osr)             # Store the OSR in Y

    irq(rel(0))             # Signal parameters read to CPU (IRQ relative to SM number)

    label("step")
    jmp(not_x, "finished")  # If X == 0 then jump to "finished"
    set(pins, 1)            # Turn pin on

    label("ondelay")
    jmp(y_dec, "ondelay")
    mov(y, osr)             # Restore the Y register (number of delay cycles)

    set(pins, 0)            # Turn pin off

    label("offdelay")
    jmp(y_dec,"offdelay")
    mov(y, osr)             # Restore the Y register (number of delay cycles)

    jmp(x_dec,"step")       # X-- then jump to "step"

    label("finished")
    set(pins, 0)            # Ensure output pin is 0 (not really needed)
    wrap()

class PulseGenerator:
    """
    A class to generate pulses using the RP2040's PIO (Programmable Input/Output) and state machines.
    Attributes:
        _sm (rp2.StateMachine): The state machine instance used for pulse generation.
        callbacks (list): A list of callback functions to be called on interrupts.
    Methods:
        __init__(_pio: int, _state_machine: int, pin: Pin):
            Initializes the PulseGenerator with the specified PIO and state machine.
        set(pps: int, pulses: int):
            Sets the pulse generator with the specified pulses per second (PPS) and number of pulses.
        callback_subscribe(callback: callable):
            Subscribes a callback function to be called on interrupts.
        __pps_to_pio_delay(pps: int) -> int:
            Converts pulses per second (PPS) to the required PIO delay.
        __interrupt_handler(sm: rp2.StateMachine):
            Handles interrupts generated by the PIO code and calls subscribed callback functions.
    """

    def __init__(self, _pio: int, _state_machine: int, step_pin: Pin):
        """
        Initializes the PulseGenerator instance.
        Args:
            _pio (int): The PIO (Programmable Input/Output) ID, must be 0 or 1.
            _state_machine (int): The state-machine ID, must be between 0 and 3.
            pin (Pin): The pin object to be used by the state machine.
        Raises:
            ValueError: If _pio is not 0 or 1.
            ValueError: If _state_machine is not between 0 and 3.
        Initializes the pulse generator on the specified PIO and state-machine,
        sets up the state machine with the given pin, and activates it. Also sets
        an interrupt handler and initializes the callback subscription list.
        """

        if _pio > 1 or _pio < 0:
            raise ValueError("PulseGenerator::__init__ - PIO ID must be 0 or 1")
        if _state_machine > 3 or _state_machine < 0:
            raise ValueError("PulseGenerator::__init__ - State-machine ID must be 0-3")

        logging.info(f"PulseGenerator::__init__ - Pulse generator initialising on PIO {_pio} state-machine {_state_machine}")
        if _pio == 1: _state_machine += 4 # PIO 0 is SM 0-3 and PIO 1 is SM 4-7

        logging.debug(f"PulseGenerator::__init__ - Micropython state-machine ID is {_state_machine}")
        self._sm = rp2.StateMachine(_state_machine, pulse_generator, freq=2500000, set_base=step_pin)
        
        # Set interrupt for SM on IRQ 0
        self._sm.irq(handler = self.__interrupt_handler)

        # Activate the state machine
        self._sm.active(1)

        # Set the callback subscription list
        self.callbacks = []

    # Set the pulse generator (and start it running)
    # PPS = Pulses Per Second, pulses = number of pulses to generate
    def set(self, pps: int, pulses: int):
        """
        Set the pulse generator parameters.
        This method configures the pulse generator by setting the pulses per second (pps)
        and the number of pulses. It calculates the delay required for the given pps and
        places the values into the TX FIFO of the state machine.
        Args:
            pps (int): Pulses per second.
            pulses (int): Number of pulses to generate.
        """

        pio_delay = self.__pps_to_pio_delay(pps)

        # Place the values into the TX FIFO towards the required state machine
        # Note: The FIFO is 4x32-bit
        #logging.debug("Pulse_generator::set: Pulses =", pulses, ", PIO delay =", pio_delay)
        self._sm.put(pulses)
        self._sm.put(pio_delay)

    # Convert pulses per second to the required PIO delay
    def __pps_to_pio_delay(self, pps: int) -> int:
        """
        Convert pulses per second (PPS) to the corresponding delay in PIO clock ticks.
        This method calculates the delay required for generating a pulse signal with the specified PPS.
        It ensures that the PPS value does not exceed the maximum allowed value of 250,000.
        The calculation takes into account the loop overhead in PIO clock ticks and the PIO clock speed.
        Args:
            pps (int): The desired pulses per second.
        Returns:
            int: The calculated delay in PIO clock ticks.
        """

        # Range check our input
        if pps > 250000:
            logging.debug("PulseGenerator::__pps_to_pio_delay: Maximum PPS is 250,000 - limiting!")
            pps = 250000
        
        # The loop overhead in PIO clock ticks
        # Note: This is dependent on the PIO code and will change if the ASM code changes
        delay_loop_overhead = 8.0

        # PIO clock speed in hertz
        pio_clock_pps = 2500000

        # Calculate the required delay and compensate for the loop overhead
        # Note: We divide the result by 2 because the delay is used for both
        # the high and low part of the signal (so it's counted twice)
        required_delay = ((pio_clock_pps / float(pps)) / 2.0) - (delay_loop_overhead / 2.0)

        return int(required_delay)

    # Allow callback subscriptions
    def callback_subscribe(self, callback):
        """
        Registers a callback function to be called when an event occurs.
        Args:
            callback (function): The callback function to be registered. 
                                 This function will be appended to the list of callbacks.
        """

        self.callbacks.append(callback)

    # Handle interrupts generated by the PIO code
    def __interrupt_handler(self, sm):
        """
        Internal method to handle interrupts.
        This method is called when an interrupt occurs. It iterates through the 
        list of callback functions stored in `self.callbacks` and executes each one.
        Args:
            sm: The state machine or context that triggered the interrupt.
        """

        # Call any functions that have subscribed to the callback
        for fn in self.callbacks:
            fn()

if __name__ == "__main__":
    from main import main
    main()