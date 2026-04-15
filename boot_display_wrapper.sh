#!/bin/bash
# Wrapper: source ROS2 + workspace so robot_msgs is importable, then run the display.
set -e
source /opt/ros/humble/setup.bash
# Source the workspace that provides robot_msgs. library_ws contains the custom msgs.
if [ -f /home/mw/yahboomcar_ros2/yahboomcar_ws/install/setup.bash ]; then
    source /home/mw/yahboomcar_ros2/yahboomcar_ws/install/setup.bash
fi
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=/home/mw/cyclonedds_unicast.xml
exec /usr/bin/python3 /home/mw/pioled_ws/boot_display.py
