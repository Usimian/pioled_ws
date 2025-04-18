# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

# progress is 0 to 100
def drawProgressbar(x, y, width, height, progress):
    bar = (width / 100) * max(min(progress, 100), 0)
    draw.rectangle((x, y, x + width - 2, y + height), outline=255, fill=0)
    draw.rectangle((x, y, x + bar, y + height), outline=None, fill=1)


while True:
    time.sleep(1)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'cut -f 1 -d " " /proc/loadavg'
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")

    cmd = "free -m"
    free_output = subprocess.check_output(cmd, shell=True).decode("utf-8")
    # Example output (second line):
    #              total        used        free      shared  buff/cache   available
    # Mem:           7972        1234        3456         123        5678        6789
    mem_line = free_output.splitlines()[1]
    mem_parts = mem_line.split()
    total_mem = int(mem_parts[1])  # in MB
    used_mem = int(mem_parts[2])   # in MB

    # Get disk usage for root filesystem and parse values as integers
    cmd = "df -h | grep ' /$'"
    df_output = subprocess.check_output(cmd, shell=True).decode("utf-8")
    # Example output: '/dev/nvme0n1p1   456G   87G  347G  20% /\n'
    parts = df_output.split()
    total_str = parts[1]  # e.g., '456G'
    used_str = parts[2]   # e.g., '87G'
    # Remove the 'G' and convert to integer (assuming GB units)
    total_gb = int(float(total_str.rstrip('G')))
    used_gb = int(float(used_str.rstrip('G')))

    # Write four lines of text.
    draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
    draw.text((x, top + 8), "CPU load: " + CPU, font=font, fill=255)
    draw.text((x, top + 16), f"{total_mem}M", font=font, fill=255)
    drawProgressbar(40, top + 18, width - 40, 6, 100*(used_mem/total_mem))  # Memory usage bar
    draw.text((x, top + 25), total_str, font=font, fill=255)
    drawProgressbar(40, top + 27, width - 40, 6, 100*(used_gb/total_gb))  # Disk usage bar
    # draw.text((x, top + 25), Disk, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.show()

