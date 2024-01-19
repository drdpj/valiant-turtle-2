/************************************************************************ 

    drivemotors.h

    Valiant Turtle 2 - Raspberry Pi Pico W Firmware
    Copyright (C) 2023 Simon Inns

    This file is part of Valiant Turtle 2

    This is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Email: simon.inns@gmail.com

************************************************************************/

#ifndef DRIVEMOTORS_H_
#define DRIVEMOTORS_H_

// Hardware mapping
// Drive motors enable - GPIO 06 (pin 9)
#define DM_ENABLE_GPIO 6

// Drive motors left step - GPIO 02 (pin 4)
// Drive motors right step - GPIO 04 (pin 6)
#define DM_LSTEP_GPIO 2
#define DM_RSTEP_GPIO 4

// Drive motors left direction - GPIO 03 (pin 5)
// Drive motors right direction - GPIO 05 (pin 7)
#define DM_LDIR_GPIO 3
#define DM_RDIR_GPIO 5

// Drive motor microstep control
#define DM_LM0_GPIO 21
#define DM_LM1_GPIO 20
#define DM_RM0_GPIO 19
#define DM_RM1_GPIO 18

// Enumerations
typedef enum {
    MOTOR_LEFT,
    MOTOR_RIGHT
} motor_side_t;

typedef enum {
    MOTOR_FORWARDS,
    MOTOR_BACKWARDS
} motor_direction_t;

typedef enum {
    MOTOR_1,    // Full step
    MOTOR_1_2,  // 1/2 step
    MOTOR_1_4,  // 1/4 step
    MOTOR_1_8   // 1/8 step
} motor_speed_t;

typedef struct stepperMotor_t {
    bool enabled;
    bool running;
    motor_speed_t speed;
    motor_direction_t direction;
    int16_t steps;
    int16_t state;
} stepperMotor_t;

void driveMotorsInitialise(void);
bool motorTimerCallback(repeating_timer_t *rt);
void driveMotorsEnable(bool state);
void driveMotorsRunning(bool state);
void driveMotorSetDir(motor_side_t side, motor_direction_t direction);
void driveMotorSetSteps(int16_t lSteps, int16_t rSteps);
void driveMotorSetSpeed(motor_side_t side, motor_speed_t speed);
void driveMotorStatus(void);

#endif /* DRIVEMOTORS_H_ */