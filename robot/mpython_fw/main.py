#************************************************************************ 
#
#   main.py
#
#   Valiant Turtle 2 - Raspberry Pi Pico W Firmware
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

from ws2812b import Ws2812b
from pen import Pen
from ina260 import Ina260
from eeprom import Eeprom
from time import sleep
from machine import I2C
from machine import Pin

# Initialise the LEDs and show some colour
leds = Ws2812b(3, 0, 7, delay=0)

# Initialise the pen control
pen = Pen(16)
pen.off()

# Initialise the I2C buses
i2c_internal = I2C(0, scl=Pin(9), sda=Pin(8), freq=100000)
i2c_external = I2C(1, scl=Pin(11), sda=Pin(10), freq=100000)

# Initialise the INA260 power monitoring chip
ina260 = Ina260(i2c_internal, 0x40)

# Initialise the EEPROM
eeprom = Eeprom(i2c_internal, 0x50)

wbuffer = bytearray([0,1,2,3,4,5,6,7,8,9])
eeprom.write(0x0, wbuffer)
print("Write Buffer = ", "".join("0x%02x " % b for b in wbuffer))
print("Read Length = ", len(wbuffer))

rbuffer = eeprom.read(0x0, 10)
print("Read Buffer = ", "".join("0x%02x " % b for b in rbuffer))
print("Read Length = ", len(rbuffer))

while True:
    leds.set_pixel(0, 255, 0, 0)
    leds.set_pixel(1, 0, 255, 0)
    leds.set_pixel(2, 0, 0, 255)
    leds.show()
    #pen.off()

    print("INA260:")
    print("  mA = ", ina260.current)
    print("  mV = ", ina260.bus_voltage)
    print("  mW = ", ina260.power)
    sleep(1.0)

    leds.set_pixel(0, 0, 255, 0)
    leds.set_pixel(1, 0, 0, 255)
    leds.set_pixel(2, 255, 0, 0)
    leds.show()
    #pen.up()
    sleep(1.0)

    leds.set_pixel(0, 0, 0, 255)
    leds.set_pixel(1, 255, 0, 0)
    leds.set_pixel(2, 0, 255, 0)
    leds.show()
    #pen.down()
    sleep(1.0)
