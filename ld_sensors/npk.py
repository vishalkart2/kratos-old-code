#!/usr/bin/env python3

import time
import serial

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

# ========== SERIAL CONFIG ==========
x = input("Enter NPK USB Port Number: ")
PORT = "/dev/ttyUSB" + x     # change if needed
BAUD = 9600
TIMEOUT = 1

# ========== MODBUS COMMANDS ==========
nitro = bytes([0x01,0x03,0x00,0x1E,0x00,0x01,0xE4,0x0C])
phos  = bytes([0x01,0x03,0x00,0x1F,0x00,0x01,0xB5,0xCC])
pota  = bytes([0x01,0x03,0x00,0x20,0x00,0x01,0x85,0xC0])
temp  = bytes([0x01,0x03,0x00,0x13,0x00,0x01,0x75,0xCF])
mois  = bytes([0x01,0x03,0x00,0x12,0x00,0x01,0x24,0x0F])
econ  = bytes([0x01,0x03,0x00,0x15,0x00,0x01,0x95,0xCE])
ph    = bytes([0x01,0x03,0x00,0x06,0x00,0x01,0x64,0x0B])

# =====================================================
def read_register(ser, cmd, name=""):
    """Read a single Modbus register (7-byte response)."""
    ser.reset_input_buffer()
    ser.write(cmd)

    resp = ser.read(7)
    if len(resp) != 7:
        print(f"❌ {name}: timeout / invalid response")
        return None

    value = (resp[3] << 8) | resp[4]

    # Reject garbage
    if value < 0 or value > 60000:
        print(f"❌ {name}: invalid value {value}")
        return None

    return value


# =====================================================
class NPKNode(Node):

    def __init__(self):
        super().__init__('npk_node')

        self.publisher_ = self.create_publisher(
            Float64MultiArray,
            'npk_data',
            10
        )

        self.timer = self.create_timer(0.1, self.timer_callback)

        # Open serial port
        self.ser = serial.Serial(
            port=PORT,
            baudrate=BAUD,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT
        )

        self.get_logger().info("NPK ROS2 node started")

    # -------------------------------------------------
    def timer_callback(self):
        moisture = read_register(self.ser, mois, "Moisture")
        temperature = read_register(self.ser, temp, "Temperature")
        ec = read_register(self.ser, econ, "EC")
        phv = read_register(self.ser, ph, "pH")
        n = read_register(self.ser, nitro, "Nitrogen")
        p = read_register(self.ser, phos, "Phosphorus")
        k = read_register(self.ser, pota, "Potassium")

        # 🚨 HARD GUARD (fixes ROS assertion crash)
        if any(v is None for v in (moisture, temperature, ec, phv, n, p, k)):
            self.get_logger().warn("Invalid sensor read, skipping publish")
            return

        # ---------- Scaling (FORCE FLOATS) ----------
        moisture_pct = float(moisture) / 10.0
        temp_c       = float(temperature) / 10.0
        ec_us        = float(ec)
        ph_val       = float(phv) / 100.0

        n_val = float(n)
        p_val = float(p)
        k_val = float(k)

        # ---------- Publish ----------
        msg = Float64MultiArray()
        msg.data = [
            moisture_pct,
            temp_c,
            ec_us,
            ph_val,
            n_val,
            p_val,
            k_val
        ]

        self.publisher_.publish(msg)

        # ---------- Print to terminal ----------
        print("====== NPK DATA ======")
        print(f"Moisture (%) : {moisture_pct:.2f}")
        print(f"Temp (C)     : {temp_c:.2f}")
        print(f"EC (uS/cm)   : {ec_us}")
        print(f"pH           : {ph_val:.2f}")
        print(f"Nitrogen     : {n_val}")
        print(f"Phosphorus   : {p_val}")
        print(f"Potassium    : {k_val}")
        print("======================\n")


# =====================================================
def main(args=None):
    rclpy.init(args=args)
    node = NPKNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.ser.close()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
