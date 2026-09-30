# ---------------------------------------------------------
# PX4-Gazebo-Criticality
#
# Base:
# Ubuntu 24.04
# ROS 2 Jazzy
# Gazebo Harmonic
# ---------------------------------------------------------

FROM ros:jazzy-ros-base

LABEL maintainer="Kailas"
LABEL project="PX4-Gazebo-Criticality"

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# ---------------------------------------------------------
# Run everything as root
# ---------------------------------------------------------

ENV HOME=/root

ENV VIRTUAL_ENV=/workspace/.venv
ENV PATH="/workspace/.venv/bin:$PATH"

# ---------------------------------------------------------
# Development Packages
# ---------------------------------------------------------

RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    zip \
    tree \
    nano \
    vim \
    build-essential \
    cmake \
    make \
    ninja-build \
    bash-completion \
    python3-pip \
    python3-venv \
    python3-colcon-common-extensions \
    python3-rosdep \
    software-properties-common \
    lsb-release \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/root && \
    touch /home/root/.bashrc

# ---------------------------------------------------------
# Gazebo Harmonic
# ---------------------------------------------------------

RUN curl -fsSL https://packages.osrfoundation.org/gazebo.gpg \
    | gpg --dearmor \
    -o /usr/share/keyrings/gazebo-archive-keyring.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/gazebo-archive-keyring.gpg] \
http://packages.osrfoundation.org/gazebo/ubuntu-stable noble main" \
> /etc/apt/sources.list.d/gazebo-stable.list

RUN apt-get update && apt-get install -y \
    gz-harmonic \
    ros-jazzy-ros-gz \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------
# Workspace Layout
# ---------------------------------------------------------

WORKDIR /workspace

RUN mkdir -p \
    /workspace/robotics \
    /workspace/micro-xrce-dds \
    /workspace/ros2_ws/src

# ---------------------------------------------------------
# Load development environment automatically
# ---------------------------------------------------------

COPY docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

RUN echo "" >> /root/.bashrc && \
    echo "# PX4-Gazebo-Criticality" >> /root/.bashrc && \
    echo "source /workspace/docker/env.sh" >> /root/.bashrc

# ---------------------------------------------------------
# Default Working Directory
# ---------------------------------------------------------

WORKDIR /workspace

ENTRYPOINT ["/entrypoint.sh"]

CMD ["bash"]
