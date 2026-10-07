# PX4-Gazebo-Criticality

A fully reproducible Docker-based development environment for generating **EuRoC-compatible safety-critical UAV datasets** using **PX4 SITL**, **ROS 2 Jazzy**, and **Gazebo Harmonic**.

The long-term objective of this project is to generate machine learning datasets for **criticality prediction** in autonomous UAV systems.

---

# Features

- Docker-based reproducible environment
- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- PX4 SITL (v1.17.0)
- Micro XRCE DDS Agent
- ROS 2 ↔ PX4 communication
- Version-locked dependencies
- Automated setup scripts
- Python virtual environment
- EuRoC dataset generation (work in progress)
- Safety-critical scenario generation (work in progress)

---

# Repository Structure

```
PX4-Gazebo-Criticality
│
├── bin/
├── docker/
├── robotics/                 # created automatically
├── micro-xrce-dds/           # created automatically
├── ros2_ws/
├── scripts/
├── setup/
├── venv/
└── README.md
```

The repository intentionally **does not** contain:

- PX4 source
- Micro XRCE DDS source
- ROS build directories
- Python virtual environment
- datasets
- logs

Everything is recreated automatically.

---

# Requirements

Host operating system

- Ubuntu 24.04 LTS

Required software

- Docker
- Docker Compose
- Git

No ROS installation is required on the host.

---

# Installation

Clone the repository

```bash
git clone <repository-url>

cd PX4-Gazebo-Criticality
```

Build the Docker image

```bash
cd docker

sudo docker compose build --no-cache

cd ..
```

Start the development container

```bash
sudo ./scripts/host/start_dev.sh
```

---

# Initial Setup

Run the following scripts **inside the container**.

```bash
cd /workspace/setup

./01_install_prerequisites.sh

./02_clone_px4.sh

./03_install_px4_dependencies.sh

./04_clone_ros_packages.sh

./05_build_ros_workspace.sh

./06_install_microxrce_agent.sh

./07_create_python_venv.sh

./08_verify_setup.sh
```

This setup only needs to be performed once.

---

# Verify Installation

Inside the container

```bash
doctor
```

All checks should pass.

---

# Running the Simulator

Open Terminal 1

```bash
./scripts/host/start_dev.sh

agent
```

Open Terminal 2

```bash
./scripts/host/start_dev.sh

sim

param set NAV_DLL_ACT 0
```

Open Terminal 3

```bash
./scripts/host/start_dev.sh

ros2 run criticality_core offboard_takeoff
```

# On each rebuild - Run these(**inside the container**):

```
cd /workspace/ros2_ws
source /opt/ros/jazzy/setup.bash
rm -rf build/px4_msgs install/px4_msgs
colcon build --symlink-install
```

---

# Current Project Status

Implemented

- Docker development environment
- ROS 2 Jazzy
- Gazebo Harmonic
- PX4 SITL
- Micro XRCE DDS Agent
- ROS workspace
- Version locking
- Automated setup scripts
- Autonomous offboard takeoff

Planned

- Mission Node
- Scenario/Event Node
- Obstacle spawning
- GPS denial
- Sensor degradation
- Battery emergency
- EuRoC dataset exporter
- criticality_labels.csv generation

---

# Repository Philosophy

Docker installs only:

- Ubuntu
- ROS 2
- Gazebo
- System dependencies

Everything project-specific is installed by the setup scripts.

This keeps Docker rebuilds fast while maintaining complete reproducibility.

---

# Tested On

Ubuntu 24.04 LTS

Docker

ROS 2 Jazzy

Gazebo Harmonic

PX4 v1.17.0

---

# License

This repository is intended for research and educational use.
