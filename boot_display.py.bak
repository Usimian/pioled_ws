#!/usr/bin/env python3
import subprocess
import time
import signal
import sys
import threading
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

STATUS_FILE = '/tmp/robot_status'

# --- OLED setup ---
i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
disp.fill(0)
disp.show()

def signal_handler(sig, frame):
    disp.fill(0)
    disp.show()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

def draw_progress_bar(x, y, w, h, pct):
    bar = (w / 100) * max(min(pct, 100), 0)
    draw.rectangle((x, y, x + w - 2, y + h), outline=255, fill=0)
    draw.rectangle((x, y, x + bar, y + h), outline=None, fill=1)

def read_status():
    try:
        with open(STATUS_FILE) as f:
            return f.read().strip() or 'Stopped'
    except FileNotFoundError:
        return 'Stopped'

# Write default status on startup
try:
    with open(STATUS_FILE, 'w') as f:
        f.write('Stopped')
except Exception:
    pass

# --- Voltage source ---
# Shared state updated by ROS2 thread when available; falls back to Rosmaster serial.
_voltage = 0.0
_voltage_lock = threading.Lock()
_ros2_active = False
_last_ros2_msg_time = 0.0

def _ros2_voltage_thread():
    """Background thread: subscribe to /robot/sensors and update _voltage."""
    global _voltage, _ros2_active
    try:
        import rclpy
        from rclpy.node import Node
        # Import the custom message — available once ROS2 workspace is sourced
        # Use a generic approach: spin and read via topic echo if import fails
        try:
            from robot_msgs.msg import SensorData
        except ImportError as e:
            print(f"[pioled] ROS2 robot_msgs import failed: {e} — will use serial fallback", flush=True)
            return

        rclpy.init()
        node = Node('pioled_voltage_reader')

        def cb(msg):
            global _voltage, _ros2_active, _last_ros2_msg_time
            with _voltage_lock:
                _voltage = msg.battery_voltage
                _ros2_active = True
                _last_ros2_msg_time = time.time()

        node.create_subscription(SensorData, '/robot/sensors', cb, 10)
        rclpy.spin(node)
        node.destroy_node()
        rclpy.shutdown()
    except Exception as e:
        print(f"[pioled] ROS2 thread error: {e}", flush=True)
    finally:
        _ros2_active = False

threading.Thread(target=_ros2_voltage_thread, daemon=True).start()

def _get_voltage_serial():
    """Read voltage from Rosmaster serial. Creates instance on first call or after failure."""
    global _bot
    try:
        if _bot is None:
            from Rosmaster_Lib import Rosmaster
            _bot = Rosmaster()
            _bot.create_receive_threading()
        return _bot.get_battery_voltage()
    except Exception:
        _bot = None
        return 0.0

_bot = None

def get_voltage():
    with _voltage_lock:
        if _ros2_active:
            return _voltage
    return _get_voltage_serial()

# Wait for network on first boot (up to 30s)
ip = 'no network'
for _ in range(30):
    ip = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode().strip()
    if ip:
        break
    time.sleep(1)

while True:
    ip = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode().strip() or 'no network'
    voltage = get_voltage()
    status = read_status()

    pct = (voltage - 9.6) * 41.67
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0,  0), status,            font=font, fill=255)
    draw.text((0, 11), f'IP: {ip}',       font=font, fill=255)
    # Consider ROS2 "active" only if a message arrived in the last 3 seconds
    with _voltage_lock:
        ros2_fresh = _ros2_active and (time.time() - _last_ros2_msg_time) < 3.0
        if not ros2_fresh:
            _ros2_active = False
    if ros2_fresh:
        try:
            r_w = int(draw.textlength('R', font=font))
        except AttributeError:
            r_w = 6
        draw.text((width - r_w - 1, 11), 'R', font=font, fill=255)
    draw.text((0, 22), f'{voltage:.1f}V', font=font, fill=255)
    draw_progress_bar(34, 23, width - 36, 8, pct)

    disp.image(image)
    disp.show()
    time.sleep(1)
