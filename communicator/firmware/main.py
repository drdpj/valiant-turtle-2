#************************************************************************ 
#
#   main.py
#
#   Valiant Turtle 2 - Communicator firmware
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

from machine import Pin, UART, I2C
from status_led import Status_led
from ir_uart import Ir_uart
from parallel_port import Parallel_port
from configuration import Configuration
from eeprom import Eeprom
from ble_central import Ble_central

from time import sleep
from micropython import const

import asyncio

# GPIO Hardware mapping
_GPIO_GREEN_LED = const(16)
_GPIO_BLUE_LED = const(18)
_GPIO_IR_LED = const(22)

_GPIO_SDA0 = const(8)
_GPIO_SCL0 = const(9)
_GPIO_SDA1 = const(10)
_GPIO_SCL1 = const(11)

_GPIO_INT0 = const(12)

_GPIO_UART0_TX = const(0)
_GPIO_UART0_RX = const(1)
_GPIO_UART1_TX = const(4)
_GPIO_UART1_RX = const(5)
_GPIO_UART1_RTS = const(7)
_GPIO_UART1_CTS = const(6)

_GPIO_BUTTON0 = const(21)
_GPIO_BUTTON1 = const(20)
_GPIO_BUTTON2 = const(19)

# # Process serial and parallel data to IR
# # using the original Valiant Turtle communication
# def legacy_mode():
#     # Send any received parallel port data via IR
#         while(parallel_port.any()):
#             blue_led.set_brightness(255)
#             ch = parallel_port.read()
#             ir_uart.ir_putc(ch)
#             #log_debug("Parallel Rx =", ch)
#             blue_led.set_brightness(0)

#         # Send any received serial data via IR
#         while(uart1.any()):
#             blue_led.set_brightness(255)
#             ch = int(uart1.read(1)[0]) # Get 1 byte, store as int
#             ir_uart.ir_putc(ch)
#             #log_debug("Serial Rx =", ch)
#             blue_led.set_brightness(0)

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

        if interval == 0: green_led.set_brightness(255)
        if interval == 5: green_led.set_brightness(10)

        if ble_central.is_peripheral_connected:
            # Stay on when connected
            if interval == 0: blue_led.set_brightness(255)
        else:
            # Flash quickly when disconnected
            if interval == 0: blue_led.set_brightness(255)
            if interval == 1: blue_led.set_brightness(0)
            if interval == 2: blue_led.set_brightness(255)
            if interval == 3: blue_led.set_brightness(0)
            if interval == 4: blue_led.set_brightness(255)
            if interval == 5: blue_led.set_brightness(0)

        # Increment interval
        interval += 1
        if interval == 6: interval = 0

        # Wait before next interval
        await asyncio.sleep_ms(250)

# Async I/O task generation and launch
async def aio_main():
    tasks = [
        # BLE related tasks
        asyncio.create_task(ble_central.ble_central_task()),

        # General background tasks
        asyncio.create_task(blue_led.led_process_task()),
        asyncio.create_task(green_led.led_process_task()),
        asyncio.create_task(status_led_task()),
    ]
    await asyncio.gather(*tasks)

# Main set up ---------------------------------------------------------------------------------------------------------

# Turn on logging
log_control(True, True, True)

# Configure serial UART0
uart0 = UART(0, baudrate=115200, tx=Pin(_GPIO_UART0_TX), rx=Pin(_GPIO_UART0_RX))

# Configure Valiant communication serial UART1
uart1 = UART(1, baudrate=4800, tx=Pin(_GPIO_UART1_TX), rx=Pin(_GPIO_UART1_RX),
    txbuf=1024, rxbuf=1024, bits=8, parity=None, stop=1)

# Ensure IR LED is off
ir_led = Pin(_GPIO_IR_LED, Pin.OUT)
ir_led.value(0)

# Configure IR UART
ir_uart = Ir_uart(_GPIO_IR_LED)

# Configure I2C interfaces
i2c0 = I2C(0, scl=Pin(_GPIO_SCL0), sda=Pin(_GPIO_SDA0), freq=400000) # Internal
i2c1 = I2C(1, scl=Pin(_GPIO_SCL1), sda=Pin(_GPIO_SDA1), freq=400000) # External

# EEPROM
eeprom = Eeprom(i2c0, 0x50)

# Configuration object
configuration = Configuration()

# Read the configuration from EEPROM
if not configuration.unpack(eeprom.read(0, configuration.pack_size)):
    # Current EEPROM image is invalid, write the default
    eeprom.write(0, configuration.pack())

# Configure Valiant communication parallel port
parallel_port = Parallel_port(i2c0, _GPIO_INT0)

# Initialise status LEDs
green_led = Status_led(_GPIO_GREEN_LED, 255, 20)
blue_led = Status_led(_GPIO_BLUE_LED, 0, 20)

# Initialise BLE central
ble_central = Ble_central()

log_info("main - Launching asynchronous tasks...")
asyncio.run(aio_main())