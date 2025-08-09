#!/usr/bin/env bash
set -e

# Source ROS 2
if [ -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]; then
  . "/opt/ros/${ROS_DISTRO}/setup.bash"
fi

# Configure Gazebo model path to include /localros and nested text_3d_models
export GAZEBO_MODEL_PATH="/localros:${GAZEBO_MODEL_PATH}"
if [ -d "/localros/text_3d_models" ]; then
  for dir in /localros/text_3d_models/*; do
    if [ -d "$dir" ]; then
      export GAZEBO_MODEL_PATH="$dir:$GAZEBO_MODEL_PATH"
    fi
  done
fi

exec "$@"


