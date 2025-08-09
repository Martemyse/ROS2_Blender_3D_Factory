# syntax=docker/dockerfile:1

# Base image
FROM ubuntu:22.04

ARG ROS_DISTRO=iron
ENV DEBIAN_FRONTEND=noninteractive \
    ROS_DISTRO=${ROS_DISTRO}

# Base tools
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# ROS 2 apt repository (keyring, no deprecated apt-key)
RUN mkdir -p /etc/apt/keyrings \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    | gpg --dearmor -o /etc/apt/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
    > /etc/apt/sources.list.d/ros2.list

# ROS 2 desktop + tools
RUN apt-get update && apt-get install -y \
    ros-${ROS_DISTRO}-desktop \
    ros-${ROS_DISTRO}-slam-toolbox \
    ros-dev-tools \
    && rm -rf /var/lib/apt/lists/*

# Gazebo (Classic)
RUN curl -sSL http://get.gazebosim.org | sh

# Minimal Python deps for geometry scripts
RUN python3 -m pip install --no-cache-dir shapely

# Runtime entrypoint to source ROS and set Gazebo paths dynamically
COPY docker/ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh

# Default workdir (customize or mount your workspace at runtime)
WORKDIR /workspace

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]

# Start from Ubuntu 22.04
FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary tools and dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    python3 \
    python3-pip \
    git

# Setup ROS 2 Iron repository
RUN curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - \
    && sh -c 'echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros2-latest.list'

# Update apt after setting up repositories
RUN apt-get update

# Install ROS 2 Iron
RUN apt-get install -y \
    ros-iron-desktop \
    ros-iron-slam-toolbox

# Install development tools for ROS 2
RUN apt-get install -y ros-dev-tools

# Install Gazebo using the provided script
RUN curl -sSL http://get.gazebosim.org | sh

# Install Python dependencies
RUN pip3 install tensorflow gym pandas

# Setup ROS 2 environment
RUN echo "source /opt/ros/iron/setup.bash" >> ~/.bashrc

# Install nano
RUN apt update && apt install -y nano

# Add paths to ~/.bashrc
RUN echo 'export GAZEBO_MODEL_PATH=/localros' >> ~/.bashrc && \
    echo 'export GAZEBO_MODEL_PATH=/localros/text_3d_models' >> ~/.bashrc && \
    echo 'for dir in /localros/text_3d_models/*; do' >> ~/.bashrc && \
    echo '    if [ -d "$dir" ]; then' >> ~/.bashrc && \
    echo '        export GAZEBO_MODEL_PATH="$dir:$GAZEBO_MODEL_PATH"' >> ~/.bashrc && \
    echo '    fi' >> ~/.bashrc && \
    echo 'done' >> ~/.bashrc

# Your ROS workspace setup and other configurations can be added here...
# WORKDIR /path/to/your/workspace

# Further setup or entry commands can be added here...

CMD ["bash"]
