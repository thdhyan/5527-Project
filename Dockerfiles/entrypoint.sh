#!/bin/bash
set -e

# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Source workspace setup if it exists
if [ -f "/ros2_ws/install/setup.bash" ]; then
  source "/ros2_ws/install/setup.bash"
fi

exec "$@"
