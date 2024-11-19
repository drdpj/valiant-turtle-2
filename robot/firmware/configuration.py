#************************************************************************ 
#
#   configuration.py
#
#   System configuration class with serialization
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

import logging
import ustruct
from micropython import const

class Configuration:
    CONFIGURATION_VERSION = const(0x03)

    def __init__(self):
        self._configuration_version = 0
        self._is_legacy_mode = False
        self._serial_speed = 0
        self._serial_rtscts = False

        # Set default configuration
        self.default()

        # ustruct format
        # See: https://docs.micropython.org/en/latest/library/struct.html
        # Format: i = 4 byte int
        # 1st int: configuration version
        # 2nd int: is legacy mode (boolean as int)
        # 3rd int: serial speed
        # 4th int: serial RTS/CTS (boolean as int)
        self.format = 'iiii'

    def pack(self) -> bytes:
        buffer = ustruct.pack(self.format,
            Configuration.CONFIGURATION_VERSION,
            int(self._is_legacy_mode),
            self._serial_speed,
            int(self._serial_rtscts)
            )
        return buffer
    
    # Unpack configuration data. Returns:
    # True = EEPROM was valid
    # False = EEPROM was invalid (uses default configuration instead)
    def unpack(self, buffer: bytes) -> bool:
        result = ustruct.unpack(self.format, buffer)

        # Place the resulting tuple into the configuration parameters
        self._configuration_version = result[0]
        self._is_legacy_mode = bool(result[1])
        self._serial_speed = result[2]
        self._serial_rtscts = bool(result[3])

        # Check configuration is valid
        if self._configuration_version != Configuration.CONFIGURATION_VERSION:
            logging.info("Configuration::unpack - Configuration invalid... Using default")
            self.default()
            return False

        logging.info("Configuration::unpack - Configuration valid")
        return True
    
    def default(self):
        self._configuration_version = Configuration.CONFIGURATION_VERSION
        self._is_legacy_mode = True
        self._serial_speed = 4800
        self._serial_rtscts = False

    # Return the size (in bytes) of the packed configuration
    @property
    def pack_size(self) -> int:
        return ustruct.calcsize(self.format)

    # Getters and setters for configuration parameters

    # Note: configuration version is read only
    @property
    def configuration_version(self) -> int:
        return self._configuration_version

    @property
    def is_legacy_mode(self) -> bool:
        return self._is_legacy_mode 
    
    @is_legacy_mode.setter
    def is_legacy_mode(self, value: bool):
        self._is_legacy_mode = value
    
    @property
    def serial_speed(self) -> int:
        return self._serial_speed
    
    @serial_speed.setter
    def serial_speed(self, value: int):
        self._serial_speed = value
    
    @property
    def serial_rtscts(self) -> bool:
        return self._serial_rtscts
    
    @serial_rtscts.setter
    def serial_rtscts(self, value: bool):
        self._serial_rtscts = value

if __name__ == "__main__":
    from main import main
    main()