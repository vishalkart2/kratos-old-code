#!/usr/bin/env python3

import serial
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

x=input("Enter USB Port number: ")
PORT = "/dev/ttyUSB"+x
BAUD = 115200


class MultiSensorNode(Node):

    def __init__(self):
        super().__init__("multi_sensor_node")

        #self.ser = serial.Serial(PORT, BAUD, timeout=1)
        #time.sleep(2)

        self.ser = serial.Serial(PORT, BAUD, timeout=1, dsrdtr=False, rtscts=False)

        # --- FORCE ESP32 RESET ---
        self.ser.setDTR(False)
        self.ser.setRTS(False)
        time.sleep(0.1)
        self.ser.setDTR(True)
        self.ser.setRTS(True)
        time.sleep(2)

        # Clear junk after reset
        self.ser.reset_input_buffer()

        self.pub_gas = self.create_publisher(Float32MultiArray, "gas_data", 20)
        self.pub_spec = self.create_publisher(Float32MultiArray, "spectral_data", 20)
        self.pub_eco2 = self.create_publisher(Float32MultiArray, "eco2_data", 20)
        self.pub_dht = self.create_publisher(Float32MultiArray, "dht_data", 20)

        self.timer = self.create_timer(0.1, self.read_serial)
        self.get_logger().info("Multi-sensor ROS2 node started")

    def read_serial(self):
        line = self.ser.readline().decode(errors="ignore").strip()
        if not line.startswith("@SENS,"):
            return

        try:
            line = line.replace("@SENS,", "")

            gas_part, rest = line.split("SPEC,", 1)
            spec_part, rest = rest.split("ECO2,", 1)
            eco2_part, dht_part = rest.split("DHT,", 1)

            gas_vals = list(map(float, gas_part.replace("GAS,", "").split(",")[:-1]))
            spec_vals = list(map(float, spec_part.split(",")[:-1]))
            eco2_vals = list(map(float, eco2_part.split(",")[:-1]))
            dht_vals = list(map(float, dht_part.split(",")))

            if len(gas_vals) != 4 or len(spec_vals) != 21 or len(eco2_vals) != 4 or len(dht_vals) != 2:
                return

            self.pub_gas.publish(Float32MultiArray(data=gas_vals))
            self.pub_spec.publish(Float32MultiArray(data=spec_vals))
            self.pub_eco2.publish(Float32MultiArray(data=eco2_vals))
            self.pub_dht.publish(Float32MultiArray(data=dht_vals))

            print("\n====== SENSOR DATA ======")
            print("Gas:", gas_vals)
            print("Spectral RGB:", spec_vals[18:21])
            print("eCO2:", eco2_vals)
            print(f"DHT: {dht_vals[0]:.2f}% {dht_vals[1]:.2f}°C")
            print("=========================")

        except Exception as e:
            self.get_logger().warn(f"Parse error: {e}")


def main():
    rclpy.init()
    node = MultiSensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.ser.close()
    rclpy.shutdown()


if __name__ == "__main__":
    main()


