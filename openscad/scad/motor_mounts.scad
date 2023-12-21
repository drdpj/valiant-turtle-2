/************************************************************************

    motor_mounts.scad
    
    Valiant Turtle 2
    Copyright (C) 2023 Simon Inns
    
    This is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    Email: simon.inns@gmail.com
    
************************************************************************/

include <BOSL/constants.scad>
use <BOSL/transforms.scad>
use <BOSL/shapes.scad>
use <BOSL/nema_steppers.scad>
use <BOSL/metric_screws.scad>

include <threaded_inserts.scad>

module nema17_motor_small()
{
    // Render the motor with the shaft pointing right and the cable to the back
    // 24mm depth with 20mm shaft
    xrot(-90) yrot(90) nema17_stepper(h=24, shaft=5, shaft_len=20, orient=ORIENT_Z);
}

module nema17_motor_large()
{
    // Render the motor with the shaft pointing right and the cable to the back
    // 48mm depth with 24mm shaft
    xrot(-90) yrot(90) nema17_stepper(h=48, shaft=5, shaft_len=24, orient=ORIENT_Z);
}

module nema17_mount()
{
    move([3.5,0,0]) {
        difference() {
            union() {
                // Faceplate top
                hull() {
                    move([0,0,11]) cuboid([7,46,24], chamfer=1, edges=EDGES_X_ALL);
                    move([-6.5,-26,-4]) cuboid([20,10,8], chamfer=1, edges=EDGES_X_ALL);
                    move([-6.5,26,-4]) cuboid([20,10,8], chamfer=1, edges=EDGES_X_ALL);
                }

                // Faceplate bottom
                hull() {
                    move([0,0,-13.5]) cuboid([7,46,14], chamfer=1, edges=EDGES_X_ALL);
                    move([0,-26,-4]) cuboid([7,10,8], chamfer=1, edges=EDGES_X_ALL);
                    move([0,26,-4]) cuboid([7,10,8], chamfer=1, edges=EDGES_X_ALL);
                }

                // Faceplate arms
                move([-20,-26,-4]) cuboid([39,10,8], chamfer=1, edges=EDGES_X_ALL);
                move([-20,26,-4]) cuboid([20,10,8], chamfer=1, edges=EDGES_X_ALL);

                // NEMA 17 Lip
                move([-(7/2) - 2.5,0,1.25]) cuboid([5,46,43.5], chamfer=1, edges=EDGES_X_ALL);
            }
            
            // Add NEMA 17 mount holes
            rotate([0,-90,0]) nema17_mount_holes(depth=8, l=0, $fn=60);

            // Chamfer the edge around the shaft
            move([7,0,0]) rotate([0,-90,0]) cyl(h=10,d=25, chamfer2=2, $fn=60);

            // Motor mounting screws through the arms
            move([-15.5 + 4,26,0]) xrot(180) cyl(h=30,d=3.25);
            move([-15.5-10,26,0]) xrot(180) cyl(h=30,d=3.25);

            move([-15.5 + 4,-26,0]) xrot(180) cyl(h=30,d=3.25);
            move([-15.5-21 + 4,-26,0]) xrot(180) cyl(h=30,d=3.25);

            // Motor mounting screw heads
            move([-15.5 + 4,26,7]) xrot(180) cyl(h=20,d=7);
            move([-15.5-10,26,2]) xrot(180) cyl(h=10,d=7);

            move([-15.5 + 4,-26,7]) xrot(180) cyl(h=20,d=7);
            move([-15.5-21 + 4,-26,2]) xrot(180) cyl(h=10,d=7);

            // Clean up for printing
            hull() {
                move([-15.5 + 4,-26,7]) xrot(180) cyl(h=20,d=7);
                move([-15.5 + 0,-26,10]) xrot(180) cyl(h=20,d=7);
            }

            hull() {
                move([-15.5 + 4,26,7]) xrot(180) cyl(h=20,d=7);
                move([-15.5 + 0,26,10]) xrot(180) cyl(h=20,d=7);
            }

            // NEMA 17 clearance
            move([-38.5,0,0]) cuboid([70,43,43]);

            // Lower mount clearance
            move([-24,-26.5,-14.99]) cuboid([38,12,14]); 
            move([-24,26.5,-14.99]) cuboid([38,12,14]); 

            // Upper clearance to avoid hitting the lower shell
            move([-10,20,31]) xrot(52) yrot(35) cuboid([48,12,14]);
            move([6,22,28]) yrot(45) xrot(-20) cuboid([48,12,14]); 
        }
    }
}

module render_motor_mounts(crend, toPrint)
{
    if (!toPrint) {
        color([0.2,0.2,0.2,1]) {
            move([98-4,64-35,-6]) nema17_mount();
            xflip() move([98-4,64-35,-6]) nema17_mount();
        }
    } else {
        move([30,0,7]) yrot(90) nema17_mount();
        xflip() move([30,0,7]) yrot(90) nema17_mount();
    }
}

module render_motor_small(crend, toPrint)
{
    if (!toPrint) {
        move([98-4,64-35,-6]) nema17_motor_small();
        xflip() move([98-4,64-35,-6]) nema17_motor_small();
    }
}

module render_motor_large(crend, toPrint)
{
    if (!toPrint) {
        move([98-4,64-35,-6]) nema17_motor_large();
        xflip() move([98-4,64-35,-6]) nema17_motor_large();
    }
}

module render_rotational_axis(crend, toPrint)
{
    if (!toPrint) {
        // Render the rotational axis to assist with the design
        move([0,64 - 35,-6]) xcyl(h=255,d=2);

        // Axis for pen
        move([0,29,44]) zcyl(h=154, d=2);
    }
}

module motor_mounts_screws()
{
    // Motors require M3x10mm screws
    move([101 - 1,13.5,9.5]) yrot(90) m3x10_screw();
    move([101 - 1,13.5+31,9.5]) yrot(90) m3x10_screw();
    move([101 - 1,13.5,-21.5]) yrot(90) m3x10_screw();
    move([101 - 1,13.5+31,-21.5]) yrot(90) m3x10_screw();

    // Body attachment requires M3x10mm screws
    move([86,3,-9]) m3x10_screw();
    move([65,3,-9]) m3x10_screw();
    move([86,55,-9]) m3x10_screw();
    move([72,55,-9]) m3x10_screw();
}

module render_motor_mounts_screws(crend, toPrint)
{
    if (!toPrint) {
        motor_mounts_screws();
        xflip() motor_mounts_screws();
    }
}