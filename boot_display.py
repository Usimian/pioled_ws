#!/usr/bin/env python3
import subprocess
import time
import signal
import sys
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from Rosmaster_Lib import Rosmaster

bot = Rosmaster()
bot.create_receive_threading()

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

BAR_WIDTH = width - 40

def draw_progress_bar(x, y, w, h, pct):
    bar = (w / 100) * max(min(pct, 100), 0)
    draw.rectangle((x, y, x + w - 2, y + h), outline=255, fill=0)
    draw.rectangle((x, y, x + bar, y + h), outline=None, fill=1)

# Wait for network on first boot (up to 30s)
ip = 'no network'
for _ in range(30):
    ip = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode().strip()
    if ip:
        break
    time.sleep(1)

while True:
    ip = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode().strip() or 'no network'
    voltage = bot.get_battery_voltage()

    pct = (voltage - 9.6) * 41.67
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0,  0), 'System Ready',         font=font, fill=255)
    draw.text((0, 11), f'IP: {ip}',            font=font, fill=255)
    draw.text((0, 22), f'{voltage:.1f}V', font=font, fill=255)
    draw_progress_bar(34, 23, width - 36, 8, pct)

    disp.image(image)
    disp.show()
    time.sleep(5)
