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

from log import log_debug, log_info, log_warn

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

class Pulse_generator:
    def __init__(self, _pio, _state_machine, pin):
        if _pio > 1 or _pio < 0:
            ValueError("Pulse_generator::__init__ - PIO ID must be 0 or 1")
        if _state_machine > 3 or _state_machine < 0:
            ValueError("Pulse_generator::__init__ - State-machine ID must be 0-3")

        log_info("Pulse_generator::__init__ - Pulse generator initialising on PIO", _pio, "state-machine", _state_machine)
        if _pio == 1: _state_machine += 4 # PIO 0 is SM 0-3 and PIO 1 is SM 4-7
        self._sm = rp2.StateMachine(_state_machine, pulse_generator, freq=2500000, set_base=Pin(pin))
        
        # Set interrupt for SM on IRQ 0
        self._sm.irq(handler = self.__interrupt_handler)

        # Activate the state machine
        self._sm.active(1)

        # Set the callback subscription list
        self.callbacks = []

    # Set the pulse generator (and start it running)
    # PPS = Pulses Per Second, pulses = number of pulses to generate
    def set(self, pps, pulses: int):
        pio_delay = self.__pps_to_pio_delay(pps)

        # Place the values into the TX FIFO towards the required state machine
        # Note: The FIFO is 4x32-bit
        #log_debug("Pulse_generator::set: Pulses =", pulses, ", PIO delay =", pio_delay)
        self._sm.put(pulses)
        self._sm.put(pio_delay)

    # Convert pulses per second to the required PIO delay
    def __pps_to_pio_delay(self, pps) -> int:
        # Range check our input
        if pps > 250000:
            log_debug("Pulse_generator::__pps_to_pio_delay: Maximum PPS is 250,000 - limiting!")
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
        self.callbacks.append(callback)

    # Handle interrupts generated by the PIO code
    def __interrupt_handler(self, sm):
        # Call any functions that have subscribed to the callback
        for fn in self.callbacks:
            fn()
