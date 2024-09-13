/************************************************************************

    connector.scad
    
    Valiant Turtle 2 - Battery Charger
    Copyright (C) 2024 Simon Inns
    
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

module connector_front()
{
    move([0,-12 + 8,46]) xrot(180) {
        male_connector_front();
    }
}

module connector_back()
{
    move([0,-12 + 8,46]) xrot(180) {
        male_connector_back();
    }
}

module male_connector_back()
{
    difference() {
        move([-23.5,19,8.125]) {
            cuboid([20,5,7.75]);
            move([0,0,6]) cuboid([10,5,5]);
        }

        // Mask for the bullet connectors (male)
        move([-23.5,16.5,10.25]) {
            move([-3,0,0]) bullet_connector_male_mask();
            move([+3,0,0]) bullet_connector_male_mask();
        }

        // Cable clearance
        move([-23.5,16.5,11.5]) {
            move([-3,0,3.5]) cyl(h=8,d=3);
            move([+3,0,3.5]) cyl(h=8,d=3);
        }

        move([-23.5,17.5,11]) {
            move([-9.25,0,0]) yrot(90) right_triangle([2.01, 12, 2.01], center=true);
            move([+9.25,0,0]) yrot(180) right_triangle([2.01, 12, 2.01], center=true);
        }
    }

    // Slots
    difference() {
        union() {
            move([-13,17.25,4.75]) cuboid([2.75,1.5,9.5]);
            move([-13 - 21,17.25,4.75]) cuboid([2.75,1.5,9.5]);
        }
        move([-23.5,16,1.25]) cuboid([20.5,8,6]);
    }
}

module male_connector_front()
{
    difference() {
        move([-23.5,19 - 4.5,8.125]) {
            cuboid([20,4,7.75]);
            move([0,0,6]) cuboid([10,4,5]);
        }

        // Mask for the bullet connectors (male)
        move([-23.5,16.5,10.25]) {
            move([-3,0,0]) bullet_connector_male_mask();
            move([+3,0,0]) bullet_connector_male_mask();
        }

        // Cable clearance
        move([-23.5,16.5,11.5]) {
            move([-3,0,3.5]) cyl(h=8,d=3);
            move([+3,0,3.5]) cyl(h=8,d=3);
        }

        move([-23.5,17.5,11]) {
            move([-9.25,0,0]) yrot(90) right_triangle([2.01, 12, 2.01], center=true);
            move([+9.25,0,0]) yrot(180) right_triangle([2.01, 12, 2.01], center=true);
        }
    }

    // Slots
    difference() {
        union() {
            move([-13,15.75,4.75]) cuboid([2.75,1.5,9.5]);
            move([-13 - 21,15.75,4.75]) cuboid([2.75,1.5,9.5]);
        }
        move([-23.5,16,1.25]) cuboid([20.5,8,6]);
    }
}

module render_connector_back(toPrint)
{
    if (!toPrint) {
        color([0.2,0.2,0.2,1]) connector_back();
    } else {
        connector_back();
    }
}

module render_connector_front(toPrint)
{
    if (!toPrint) {
        color([0.2,0.2,0.2,1]) connector_front();
    } else {
        connector_front();
    }
}