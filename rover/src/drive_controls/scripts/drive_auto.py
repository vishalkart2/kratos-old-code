#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist
import math


class Drive(Node):
    def __init__(self):
        super().__init__('drive_node')

        # Physical parameters
        self.WHEEL_RADIUS = 0.075   # meters (placeholder value)
        self.TRACK_WIDTH = 0.50     # meters (placeholder value)
        self.MAX_RPM = 70.0

        # Latest commanded velocities
        self.v = 0.0        # m/s
        self.omega = 0.0    # rad/s

        # Subscribe to cmd_vel
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel_true',
            self.cmd_callback,
            10
        )

        # Publish wheel commands
        self.publisher = self.create_publisher(
            Float32MultiArray,
            '/rover',
            10
        )

        self.timer = self.create_timer(0.1, self.timer_callback)

        self.msg = Float32MultiArray()
        self.msg.data = [0.0] * 6

    def cmd_callback(self, msg: Twist):
        self.v = msg.linear.x
        self.omega = msg.angular.z*5

    def timer_callback(self):
        wheel_cmds = self.move(self.v, self.omega)
        self.msg.data = wheel_cmds
        self.publisher.publish(self.msg)

    def compute_side_rpm(self, v, omega):
        # Differential drive kinematics
        v_r = v + omega * self.TRACK_WIDTH / 2.0
        v_l = v - omega * self.TRACK_WIDTH / 2.0

        # Convert linear wheel speed to RPM
        rpm_r = (v_r * 60.0) / (2.0 * math.pi * self.WHEEL_RADIUS)
        rpm_l = (v_l * 60.0) / (2.0 * math.pi * self.WHEEL_RADIUS)

        # Enforce motor speed limit
        max_rpm = max(abs(rpm_r), abs(rpm_l))
        if max_rpm > self.MAX_RPM:
            scale = self.MAX_RPM / max_rpm
            rpm_r *= scale
            rpm_l *= scale

        return rpm_r, rpm_l

    def move(self, v, omega): 
        velx, velz = self.compute_side_rpm(v, omega)

        # NOTE:
        # velx / velz are side RPMs.
 

        print(velx, " ", velz)
        # right_wheel_front = 0.0

        left_wheel_front = 0.0
        right_wheel_front = 0.0
        right_wheel_mid = 0.0
        left_wheel_mid = 0.0
        right_wheel_back = 0.0
        left_wheel_back = 0.0

        if (velx >= 0 and velz >= 0):
            left_wheel_front = ((velx+velz)/2+(velx-velz)/2) * 0.56
            right_wheel_front = ((velx+velz)/2-(velx-velz)/2) * 0.62
            right_wheel_mid = ((velx+velz)/2+(velx-velz)/2) * 0.63
            left_wheel_mid = ((velx+velz)/2-(velx-velz)/2) * 0.55
            right_wheel_back = ((velx+velz)/2+(velx-velz)/2) * 0.64
            left_wheel_back = ((velx+velz)/2-(velx-velz)/2) * 0.59
        
        elif (velx <= 0 and velz <= 0):

            right_wheel_front = ((velx+velz)/2+(velx-velz)/2) * 0.59
            left_wheel_front = ((velx+velz)/2-(velx-velz)/2) * 0.59
            right_wheel_mid = ((velx+velz)/2+(velx-velz)/2) * 0.58
            left_wheel_mid = ((velx+velz)/2-(velx-velz)/2) * 0.59
            right_wheel_back = ((velx+velz)/2+(velx-velz)/2) * 0.63
            left_wheel_back = ((velx+velz)/2-(velx-velz)/2) * 0.61
        
        elif (velx >= 0 and velz <= 0):
            right_wheel_front = ((velx+velz)/2+(velx-velz)/2) * 0.62
            left_wheel_front = ((velx+velz)/2-(velx-velz)/2)  * 0.59
            right_wheel_mid = ((velx+velz)/2+(velx-velz)/2) * 0.63
            left_wheel_mid = ((velx+velz)/2-(velx-velz)/2)  * 0.59
            right_wheel_back = ((velx+velz)/2+(velx-velz)/2) * 0.64
            left_wheel_back = ((velx+velz)/2-(velx-velz)/2) * 0.61
         
        elif (velx <= 0 and velz >= 0):
            right_wheel_front = ((velx+velz)/2+(velx-velz)/2) * 0.59
            left_wheel_front = ((velx+velz)/2-(velx-velz)/2)  * 0.56 
            right_wheel_mid = ((velx+velz)/2+(velx-velz)/2) * 0.58
            left_wheel_mid = ((velx+velz)/2-(velx-velz)/2) *0.55
            right_wheel_back = ((velx+velz)/2+(velx-velz)/2)  * 0.63
            left_wheel_back = ((velx+velz)/2-(velx-velz)/2)  * 0.59
           
        else:  # velx == 0 and velz == 0
            right_wheel_front = 0
            left_wheel_front = 0
            right_wheel_mid = 0
            left_wheel_mid = 0
            right_wheel_back = 0
            left_wheel_back = 0

        # List of all wheel speeds
        wheel_speeds = [
            right_wheel_front,
            left_wheel_front,
            right_wheel_mid,
            left_wheel_mid,
            right_wheel_back,
            left_wheel_back,
        ]


        return right_wheel_front, left_wheel_front, right_wheel_mid, left_wheel_mid, right_wheel_back, left_wheel_back


def main(args=None):
    rclpy.init(args=args)
    node = Drive()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
