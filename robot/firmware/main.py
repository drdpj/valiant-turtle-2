#************************************************************************ 
#
#   main.py
#
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

from log import log_debug, log_info, log_warn, log_control

from pen import Pen
from ina260 import Ina260
from eeprom import Eeprom
from configuration import Configuration
from velocity import Velocity
from drv8825 import Drv8825
from stepper import Stepper
from metric import Metric
from ble_peripheral import Ble_peripheral
from led_fx import Led_fx

from time import sleep
from machine import I2C, Pin

import asyncio

# GPIO hardware mapping
_GPIO_LEDS = const(7)
_GPIO_PEN = const(16)

_GPIO_SDA0 = const(8)
_GPIO_SCL0 = const(9)
_GPIO_SDA1 = const(10)
_GPIO_SCL1 = const(11)

_GPIO_LM_STEP = const(2)
_GPIO_RM_STEP = const(3)
_GPIO_LM_DIR = const(4)
_GPIO_RM_DIR = const(5)
_GPIO_ENABLE = const(6)
_GPIO_M0 = const(12)
_GPIO_M1 = const(13)
_GPIO_M2 = const(14)

# WS2812b led number mapping
_LED_power = const(0)
_LED_left_motor = const(1)
_LED_right_motor = const(2)
_LED_left_eye = const(3)
_LED_right_eye = const(4)

# Async task to update status LEDs depending on various states and times
async def status_led_task():
    interval = 0

    while True:
        # interval 0 =    0
        # interval 1 =  250
        # interval 2 =  500
        # interval 3 =  750
        # interval 4 = 1000
        # interval 5 = 1250

        # Stepper motor status
        if left_stepper.is_busy:
            led_fx.set_led_colour(_LED_left_motor, 64, 0, 0)
        else:
            led_fx.set_led_colour(_LED_left_motor, 0, 64, 0)

        if right_stepper.is_busy:
            led_fx.set_led_colour(_LED_right_motor, 64, 0, 0)
        else:
            led_fx.set_led_colour(_LED_right_motor, 0, 64, 0)

        # Eyes
        if ble_peripheral.is_connected:
            led_fx.set_led_colour(_LED_left_eye, 0, 0, 64)
            led_fx.set_led_colour(_LED_right_eye, 0, 0, 64)
        else:
            led_fx.set_led_colour(_LED_left_eye, 0, 64, 0)
            led_fx.set_led_colour(_LED_right_eye, 0, 64, 0)

        # Power LED
        if interval == 0: 
            led_fx.set_led_colour(_LED_power, 0, 64, 0)
        if interval == 5: 
            led_fx.set_led_colour(_LED_power, 64, 0, 64)

        interval += 1
        if interval == 6: interval = 0

        # Wait before next interval
        await asyncio.sleep_ms(250)

# Output power monitoring information periodically
ina260_ticker = 0
def ina260_info():
    global ina260_ticker
    if ina260_ticker == 0:
        log_info("INA260: mA =", ina260.current, "/ mV =" , ina260.bus_voltage, "/ mW =", ina260.power)
    ina260_ticker += 1
    if ina260_ticker == 2000: ina260_ticker = 0

# Async I/O task generation and launch
async def aio_main():
    tasks = [
        # BLE tasks
        asyncio.create_task(ble_peripheral.ble_peripheral_task()),

        # General background tasks
        asyncio.create_task(status_led_task()),
        asyncio.create_task(led_fx.process_leds_task()),
    ]
    await asyncio.gather(*tasks)

# Main set up ---------------------------------------------------------------------------------------------------------

# Turn on logging
log_control(True, True, True)

# Initialise the pen control
pen = Pen(_GPIO_PEN)
pen.off()

# Initialise the I2C buses
i2c_internal = I2C(0, scl=Pin(_GPIO_SCL0), sda=Pin(_GPIO_SDA0), freq=400000)
i2c_external = I2C(1, scl=Pin(_GPIO_SCL1), sda=Pin(_GPIO_SDA1), freq=400000)

# Initialise the INA260 power monitoring chip
ina260 = Ina260(i2c_internal, 0x40)

# Initialise the EEPROM
eeprom = Eeprom(i2c_internal, 0x50)

# Read the configuration from EEPROM
configuration = Configuration()
if not configuration.unpack(eeprom.read(0, configuration.pack_size)):
    # Current EEPROM image is invalid, write the default
    eeprom.write(0, configuration.pack())

# Initialise BLE peripheral
ble_peripheral = Ble_peripheral()

# Configure the DRV8825
drv8825 = Drv8825(_GPIO_ENABLE, _GPIO_M0, _GPIO_M1, _GPIO_M2)
drv8825.set_steps_per_revolution(800)
drv8825.set_enable(False)

# Configure the steppers
left_stepper = Stepper(_GPIO_LM_DIR, _GPIO_LM_STEP, True)
left_stepper.set_forwards()
right_stepper = Stepper(_GPIO_RM_DIR, _GPIO_RM_STEP, False)
right_stepper.set_forwards()

# Configure the LEDs
led_fx = Led_fx(5, _GPIO_LEDS)

# Define a velocity sequence
# velocity = Velocity(6400, 32, 2, 1600, 16)

# while True:
#     drv8825.set_enable(True)
#     left_stepper.set_velocity(velocity)
#     right_stepper.set_velocity(velocity)
#     print("Stepper sequence running")

#     # Wait for the stepper to finish
#     while left_stepper.is_busy or right_stepper.is_busy:
#         sleep(0.01)
#     drv8825.set_enable(False)
#     print("Stepper sequence complete")

log_info("main - Launching asynchronous tasks...")
asyncio.run(aio_main())