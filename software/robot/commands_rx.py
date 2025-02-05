#************************************************************************ 
#
#   commands_rx.py
#
#   Command handling for the Valiant Turtle 2 robot
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

import picolog
import asyncio

from pen import Pen
from ina260 import Ina260
from eeprom import Eeprom
from configuration import Configuration
from led_fx import LedFx
from diffdrive import DiffDrive

# WS2812b led number mapping
_LED_status = const(0)
_LED_left_motor = const(1)
_LED_right_motor = const(2)
_LED_right_eye = const(3)
_LED_left_eye = const(4)

class CommandsRx:
    def __init__(self, pen :Pen, ina260 :Ina260, eeprom :Eeprom, led_fx :LedFx, diff_drive :DiffDrive, configuration :Configuration):
        self._pen = pen
        self._ina260 = ina260
        self._eeprom = eeprom
        self._led_fx = led_fx
        self._diff_drive = diff_drive
        self._configuration = configuration

    @property
    def motors_enabled(self) -> bool:
        return self._diff_drive.is_enabled
    
    # Convert between mm and um
    def __mm_to_um(self, mm: float) -> int:
        return int(mm * 1000)
    
    # Convert between um and mm
    def __um_to_mm(self, um: float) -> float:
        return um / 1000

    async def motors(self, enable: bool):
        picolog.info(f"CommandsRx::motors - {'Enabling' if enable else 'Disabling'} motors")
        if enable:
            # Enable the motors and reset the origin to the current position
            self._diff_drive.set_enable(True)
            self._diff_drive.reset_origin()
        else:
            self._diff_drive.set_enable(False)

    async def forward(self, distance_mm: float) -> tuple[float, float, float]:
        picolog.info(f"CommandsRx::forward - Moving forward {distance_mm} mm")
        self._diff_drive.drive_forward(self.__mm_to_um(distance_mm))
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)

        # Return the new position and heading
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        heading = self._diff_drive.get_heading()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2), round(heading, 2)

    async def backward(self, distance_mm: float) -> tuple[float, float, float]:
        picolog.info(f"CommandsRx::backward - Moving backward {distance_mm} mm")
        self._diff_drive.drive_backward(self.__mm_to_um(distance_mm))
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)
        
        # Return the new position and heading
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        heading = self._diff_drive.get_heading()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2), round(heading, 2)

    async def left(self, angle_degrees: float) -> tuple[float, float, float]:
        picolog.info(f"CommandsRx::left - Turning left {angle_degrees} degrees")
        self._diff_drive.turn_left(angle_degrees)
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)

        # Return the new position and heading
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        heading = self._diff_drive.get_heading()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2), round(heading, 2)

    async def right(self, angle_degrees: float) -> tuple[float, float, float]:
        picolog.info(f"CommandsRx::right - Turning right {angle_degrees} degrees")
        self._diff_drive.turn_right(angle_degrees)
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)

        # Return the new position and heading
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        heading = self._diff_drive.get_heading()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2), round(heading, 2)

    async def circle(self, radius_mm: float, extent_degrees: float) -> tuple[float, float, float]:
        picolog.info(f"CommandsRx::circle - Circle with radius {radius_mm} mm and extent of {extent_degrees} degrees")
        self._diff_drive.circle(self.__mm_to_um(radius_mm), extent_degrees)
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)

        # Return the new position and heading
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        heading = self._diff_drive.get_heading()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2), round(heading, 2)

    async def setheading(self, heading_degrees: float):
        picolog.info(f"CommandsRx::setheading - Setting heading to {heading_degrees} degrees")
        self._diff_drive.set_heading(heading_degrees)
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)

    async def setx(self, x_mm: float) -> tuple[float, float, float]:
        picolog.info(f"CommandsRx::setx - Setting X position to {x_mm} mm")
        self._diff_drive.set_cartesian_x_position(self.__mm_to_um(x_mm))
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)

        # Return the new position and heading
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        heading = self._diff_drive.get_heading()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2), round(heading, 2)

    async def sety(self, y_mm: float) -> tuple[float, float, float]:
        picolog.info(f"CommandsRx::sety - Setting Y position to {y_mm} mm")
        self._diff_drive.set_cartesian_y_position(self.__mm_to_um(y_mm))
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)

        # Return the new position and heading
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        heading = self._diff_drive.get_heading()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2), round(heading, 2)

    async def setposition(self, x_mm: float, y_mm: float) -> tuple[float, float, float]:
        picolog.info(f"CommandsRx::setposition - Setting position to ({x_mm}, {y_mm}) mm")
        self._diff_drive.set_cartesian_position(self.__mm_to_um(x_mm), self.__mm_to_um(y_mm))
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)

        # Return the new position and heading
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        heading = self._diff_drive.get_heading()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2), round(heading, 2)

    async def towards(self, x_mm: float, y_mm: float) -> tuple[float, float, float]:
        picolog.info(f"CommandsRx::towards - Turning towards ({x_mm}, {y_mm}) mm")
        self._diff_drive.turn_towards_cartesian_point(self.__mm_to_um(x_mm), self.__mm_to_um(y_mm))
        while self._diff_drive.is_moving:
            await asyncio.sleep(0.25)

        # Return the new position and heading
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        heading = self._diff_drive.get_heading()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2), round(heading, 2)

    async def reset_origin(self):
        picolog.info("CommandsRx::reset_origin - Resetting origin")
        self._diff_drive.reset_origin()
        return

    async def heading(self) -> float:
        picolog.info("CommandsRx::heading - Getting heading")
        return round(self._diff_drive.get_heading(), 2)

    async def position(self) -> tuple[float, float]:
        picolog.info("CommandsRx::position - Getting position")
        x_pos_um, y_pos_um = self._diff_drive.get_cartesian_position()
        return round(self.__um_to_mm(x_pos_um), 2), round(self.__um_to_mm(y_pos_um), 2)

    async def penup(self):
        picolog.info(f"CommandsRx::penup - Raising pen")
        self._pen.up()
        return
    
    async def pendown(self):
        picolog.info(f"CommandsRx::pendown - Lowering pen")
        self._pen.down()
        return

    async def isdown(self) -> bool:
        picolog.info("CommandsRx::isdown - Getting pen state")
        return not self._pen.is_servo_up

    async def eyes(self, eye: int, red: int, green: int, blue: int):
        if eye == 0:
            picolog.info(f"CommandsRx::eyes - Setting both eyes to colour ({red}, {green}, {blue})")
            self._led_fx.set_led_colour(_LED_left_eye, red, green, blue)
            self._led_fx.set_led_colour(_LED_right_eye, red, green, blue)
        elif eye == 1:
            picolog.info(f"CommandsRx::eyes - Setting left eye colour to ({red}, {green}, {blue})")
            self._led_fx.set_led_colour(_LED_left_eye, red, green, blue)
        else:
            picolog.info(f"CommandsRx::eyes - Setting right eye colour to ({red}, {green}, {blue})")
            self._led_fx.set_led_colour(_LED_right_eye, red, green, blue)

    async def power(self) -> tuple[int, int, int]:
        mv = int(self._ina260.voltage_mV)
        ma = int(self._ina260.current_mA)
        mw = int(self._ina260.power_mW)

        picolog.info(f"CommandsRx::power - Power readings: {mv} mV, {ma} mA, {mw} mW")
        return mv, ma, mw
    
    async def set_linear_velocity(self, target_speed_mms: int, acceleration_mmpss: int):
        picolog.info(f"CommandsRx::set_linear_velocity - Setting linear target speed to {target_speed_mms} mm/s and acceleration to {acceleration_mmpss} mm/s^2")
        self._diff_drive.set_linear_velocity(self.__mm_to_um(target_speed_mms), self.__mm_to_um(acceleration_mmpss))
        self._configuration.linear_target_speed_umps = self.__mm_to_um(target_speed_mms)
        self._configuration.linear_acceleration_umpss = self.__mm_to_um(acceleration_mmpss)

    async def set_rotational_velocity(self, target_speed_mms: int, acceleration_mmps: int):
        picolog.info(f"CommandsRx::set_rotational_velocity - Setting rotational target speed to {target_speed_mms} mm/s and acceleration to {acceleration_mmps} mm/s^2")
        self._diff_drive.set_rotational_velocity(self.__mm_to_um(target_speed_mms), self.__mm_to_um(acceleration_mmps))
        self._configuration.rotational_target_speed_umps = self.__mm_to_um(target_speed_mms)
        self._configuration.rotational_acceleration_umpss = self.__mm_to_um(acceleration_mmps)

    async def get_linear_velocity(self) -> tuple[float, float]:
        picolog.info("CommandsRx::get_linear_velocity - Getting linear velocity")
        target_speed_ums, acceleration_umpss = self._diff_drive.get_linear_velocity()
        return (self.__um_to_mm(target_speed_ums), self.__um_to_mm(acceleration_umpss))
    
    async def get_rotational_velocity(self) -> tuple[float, float]:
        picolog.info("CommandsRx::get_rotational_velocity - Getting rotational velocity")
        target_speed_ums, acceleration_umpss = self._diff_drive.get_rotational_velocity()
        return (self.__um_to_mm(target_speed_ums), self.__um_to_mm(acceleration_umpss))
        
    async def set_wheel_diameter_calibration(self, calibration_um: int):
        picolog.info(f"CommandsRx::set_wheel_diameter_calibration - Setting wheel diameter calibration to {calibration_um} um")
        self._diff_drive.set_wheel_calibration(calibration_um)
        self._configuration.wheel_calibration_um = calibration_um

    async def set_axel_distance_calibration(self, calibration_um: int):
        picolog.info(f"CommandsRx::set_axel_distance_calibration - Setting axel distance calibration to {calibration_um} um")
        self._diff_drive.set_axel_calibration(calibration_um)
        self._configuration.axel_calibration_um = calibration_um

    async def get_wheel_diameter_calibration(self) -> int:
        picolog.info("CommandsRx::get_wheel_diameter_calibration - Getting wheel diameter calibration")
        return self._diff_drive.get_wheel_calibration()
    
    async def get_axel_distance_calibration(self) -> int:
        picolog.info("CommandsRx::get_axel_distance_calibration - Getting axel distance calibration")
        return self._diff_drive.get_axel_calibration()
    
    async def set_turtle_id(self, turtle_id: int):
        picolog.info(f"CommandsRx::set_turtle_id - Setting turtle ID to {turtle_id}")
        self._configuration.turtle_id = turtle_id

    async def get_turtle_id(self) -> int:
        picolog.info("CommandsRx::get_turtle_id - Getting turtle ID")
        return self._configuration.turtle_id

    async def load_config(self):
        picolog.info("CommandsRx::load_config - Loading configuration")
        self._configuration.unpack(self._eeprom.read(0, self._configuration.pack_size))
        self._diff_drive.set_linear_velocity(self._configuration.linear_target_speed_umps, self._configuration.linear_acceleration_umpss)
        self._diff_drive.set_rotational_velocity(self._configuration.rotational_target_speed_umps, self._configuration.rotational_acceleration_umpss)
        self._diff_drive.set_wheel_calibration(self._configuration.wheel_calibration_um)
        self._diff_drive.set_axel_calibration(self._configuration.axel_calibration_um)

    async def save_config(self):
        picolog.info("CommandsRx::save_config - Saving configuration")
        self._eeprom.write(0, self._configuration.pack())

    async def reset_config(self):
        picolog.info("CommandsRx::reset_config - Resetting configuration to default")
        self._configuration.default()
        self._diff_drive.set_linear_velocity(self._configuration.linear_target_speed_umps, self._configuration.linear_acceleration_umpss)
        self._diff_drive.set_rotational_velocity(self._configuration.rotational_target_speed_umps, self._configuration.rotational_acceleration_umpss)
        self._diff_drive.set_wheel_calibration(self._configuration.wheel_calibration_um)
        self._diff_drive.set_axel_calibration(self._configuration.axel_calibration_um)

if __name__ == "__main__":
    from main import main
    main()