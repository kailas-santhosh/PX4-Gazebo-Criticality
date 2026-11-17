# PX4-Gazebo-Criticality

A Docker-based research framework for developing and evaluating **safety-critical scenarios for autonomous UAV navigation** using **PX4 SITL**, **ROS 2 Jazzy**, and **Gazebo Harmonic**.

The project combines a simulated x500 quadrotor, ROS 2 mission and scenario logic, controlled criticality-event injection, and multimodal dataset logging. Its purpose is to support repeatable experiments for autonomous navigation, robustness evaluation, safety-critical perception, and future learning-based approaches.

> **Dataset terminology:** The logger uses a EuRoC-inspired sequence layout. The current output should not be described as fully EuRoC-compatible: it is a monocular simulation dataset with project-specific event labels and timestamp conventions, and it does not currently provide the complete calibration and metadata package of the original EuRoC dataset.

---

## Contents

- [Project goals](#project-goals)
- [Current implementation status](#current-implementation-status)
- [System architecture](#system-architecture)
- [Repository layout](#repository-layout)
- [Environment and pinned dependencies](#environment-and-pinned-dependencies)
- [Continue from the current installation checkpoint](#continue-from-the-current-installation-checkpoint)
- [Build after changing code](#build-after-changing-code)
- [Run a simulation](#run-a-simulation)
- [Scenario configuration](#scenario-configuration)
- [Criticality events](#criticality-events)
- [Dataset generation](#dataset-generation)
- [Useful development commands](#useful-development-commands)
- [Troubleshooting](#troubleshooting)
- [Research and real-world relevance](#research-and-real-world-relevance)
- [Limitations and next development steps](#limitations-and-next-development-steps)
- [Contributing and reproducibility](#contributing-and-reproducibility)
- [Push your changes to GitHub](#push-your-changes-to-github)
- [License](#license)

---

## Project goals

The central goal is to create a controllable simulation framework in which researchers can specify **what critical event occurs, when it occurs, where it occurs, and what the simulated UAV observes while it occurs**.

The framework is intended to help generate datasets for questions such as:

- How does a UAV's navigation/perception system respond when a visual sensor becomes degraded?
- What happens to a mission when GPS information becomes unavailable or unreliable?
- How does the vehicle behave when an obstacle is introduced into its path?
- Can sensor and vehicle-state measurements be associated with accurately recorded event intervals?
- Can controlled scenario variations be used to evaluate robustness across repeated simulation runs?

The long-term direction is a scenario-generation platform capable of producing large numbers of labeled, reproducible flights. Automated large-scale scenario sampling and reinforcement-learning training are future directions, not claims about the current implementation.

## Current implementation status

The repository snapshot supplied with this README contains the following implementation.

### Implemented in the repository

- Docker development environment based on Ubuntu 24.04 / ROS 2 Jazzy.
- Gazebo Harmonic and ROS-Gazebo bridge integration.
- PX4 SITL setup scripts with a pinned PX4 revision.
- Micro XRCE-DDS Agent setup and PX4-to-ROS 2 communication.
- ROS 2 Python package `criticality_core`.
- PX4 offboard controller and square waypoint mission components.
- Scenario configuration loading and validation.
- Zone-based and time-based trigger classes.
- Event base class, event manager and event factory.
- Obstacle, GPS, sensor-degradation and battery event classes.
- Gazebo model-management utilities and SDF models.
- Camera degradation processing components.
- Moving-target simulator and moving-target navigation components.
- Dataset session and sequence management.
- Camera image, IMU and vehicle-state logging components.
- Criticality event-label CSV generation.
- Tests for selected logger, obstacle-coordinate and event-lifecycle behavior.

### Important distinctions

The presence of a class or configuration option in the repository does not, by itself, prove that its full physical effect has been experimentally validated. In particular:

- The supplied `default_scenario.yaml` currently configures a single obstacle event.
- `default_scenario_overlap.yaml` contains a broader multi-event configuration, including overlapping spatial triggers and a time-triggered camera event.
- The scenario runner currently loads `default_scenario.yaml` by name. Selecting another configuration may require changing the loader invocation or adding a configuration-selection mechanism.
- Moving-target components exist, but the default scenario is configured for fixed-waypoint navigation.
- GPS, gyro and battery event code paths require event-aligned run evidence before claiming a measured vehicle/sensor response.
- `random_target_navigation.py` is present but empty in the supplied repository snapshot.
- Automated randomized scenario generation, large-scale batch generation and RL training are not implemented in this snapshot.

Use the source and evidence level carefully when describing results.

---

## System architecture

The system has three main software environments that communicate through defined interfaces.

### 1. PX4 SITL — flight control

PX4 runs the simulated flight controller for the x500 vehicle. The ROS 2 offboard controller sends setpoints and vehicle commands. PX4 remains responsible for flight-control execution and vehicle stabilization.

The PX4/ROS 2 data path is:

```text
PX4 uORB messages
       |
PX4 uXRCE-DDS client
       |
UDP / XRCE-DDS transport
       |
Micro XRCE-DDS Agent
       |
DDS / ROS 2 topics
       |
ROS 2 project nodes
```

### 2. Gazebo Harmonic — simulated world

Gazebo simulates the environment, vehicle model, camera and spawned entities. The ROS-Gazebo bridge exposes selected Gazebo Transport messages to ROS 2.

```text
Gazebo Transport
       |
ros_gz_bridge
       |
ROS 2 topics
       |
Camera processing / logging / project nodes
```

### 3. ROS 2 Jazzy — project logic

The ROS 2 workspace hosts independent Python nodes. The main responsibilities are separated:

| Component | Responsibility |
|---|---|
| `OffboardTakeoff` | Offboard heartbeat, setpoints, arming and takeoff/mission control |
| `ScenarioRunner` | Loads scenario configuration, tracks telemetry, evaluates triggers and coordinates events |
| Trigger classes | Decide whether a configured event should activate |
| Event manager/factory | Creates and manages event objects |
| Event classes | Execute obstacle, GPS, sensor and battery event behavior |
| `EntityManager` and utilities | Spawn, move and remove Gazebo models |
| Camera components | Apply configured image degradation and publish processed images |
| `DatasetLogger` | Subscribes to camera, IMU, position and attitude streams |
| `EuRoCLogger` | Writes camera images and CSV measurement streams |
| `CriticalityLogger` | Records event onset/offset and selected telemetry context |
| `SequenceManager` | Creates the sequence directory structure |

ROS nodes communicate through ROS topics rather than sharing Python objects across process boundaries. Each logger/runner maintains its own local telemetry snapshot.

---

## Repository layout

```text
PX4-Gazebo-Criticality/
├── bin/
│   └── start_container
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── env.sh
├── ros2_ws/
│   └── src/
│       └── criticality_core/
│           ├── config/
│           │   ├── default_scenario.yaml
│           │   └── default_scenario_overlap.yaml
│           ├── criticality_core/
│           │   ├── configuration/
│           │   ├── controllers/
│           │   ├── events/
│           │   ├── logging/
│           │   ├── missions/
│           │   ├── navigation/
│           │   ├── px4/
│           │   ├── scenarios/
│           │   ├── sensors/
│           │   ├── triggers/
│           │   ├── utilities/
│           │   └── utils/
│           ├── launch/
│           ├── models/
│           ├── test/
│           ├── worlds/
│           ├── package.xml
│           └── setup.py
├── scripts/
│   ├── container/
│   │   ├── build.sh
│   │   ├── clean.sh
│   │   ├── doctor.sh
│   │   ├── run_sim.sh
│   │   └── workspace.sh
│   └── host/
│       ├── start_dev.sh
│       └── stop_dev.sh
├── setup/
│   ├── 00_common.sh
│   ├── 01_install_prerequisites.sh
│   ├── 02_clone_px4.sh
│   ├── 03_install_px4_dependencies.sh
│   ├── 04_clone_ros_packages.sh
│   ├── 05_build_ros_workspace.sh
│   ├── 06_install_microxrce_agent.sh
│   ├── 07_create_python_venv.sh
│   ├── 08_verify_setup.sh
│   ├── issues_faced.txt
│   └── versions.txt
├── venv/
│   └── requirements.txt
├── .gitignore
└── README.md
```

### Generated locally (not committed)

The setup scripts create/download/build dependencies that are intentionally excluded from the Git repository:

```text
robotics/
└── PX4-Autopilot/

micro-xrce-dds/
└── Micro-XRCE-DDS-Agent/

ros2_ws/
├── build/
├── install/
└── log/

.venv/
datasets/
logs/
output/
```

Do not commit PX4 source, Micro XRCE-DDS Agent source, ROS build/install/log directories, virtual environments, generated datasets or runtime logs unless the repository's storage policy is deliberately changed.

---

## Environment and pinned dependencies

The project is configured around:

| Component | Version / configuration |
|---|---|
| Host OS | Ubuntu 24.04 LTS |
| Container base | `ros:jazzy-ros-base` |
| ROS 2 | Jazzy |
| Simulator | Gazebo Harmonic |
| Flight controller | PX4 SITL |
| PX4 revision | Tag `v1.17.0`, pinned commit in `setup/versions.txt` |
| PX4 vehicle | x500 with monocular camera model (`gz_x500_mono_cam`) |
| ROS language API | Python 3 / `rclpy` |
| PX4/ROS bridge | PX4 uXRCE-DDS client and Micro XRCE-DDS Agent |
| Gazebo/ROS bridge | `ros_gz_bridge` |
| Image processing | OpenCV, `cv_bridge`, NumPy |

The exact PX4, `px4_msgs`, `px4_ros_com` and Micro XRCE-DDS Agent commits are recorded in `setup/versions.txt`. Treat that file as the source of truth for the repository's pinned revisions.

### Host requirements

- Ubuntu 24.04 LTS
- Git
- Docker Engine
- Docker Compose plugin
- A graphical display session for Gazebo GUI
- `xhost` for the current X11-based GUI forwarding setup

ROS 2 and Gazebo do not need to be installed natively on the host when using the supplied container.

---

## Continue from the current installation checkpoint

This section is for a developer who has already cloned the repository and completed most or all of the initial dependency installation.

**Do not rerun the full setup sequence just because you are returning to the project.** First check whether the local generated dependencies and ROS workspace are still present.

### Step 1 — Open the cloned repository

On the Ubuntu host:

```bash
cd ~/Desktop/Github/PX4-Gazebo-Criticality
```

Check the repository state:

```bash
git status
git branch --show-current
```

### Step 2 — Start or enter the development container

```bash
./scripts/host/start_dev.sh
```

This script checks Docker and the display environment, grants local Docker X11 access, starts the Compose service, and opens a shell in the development container.

The project directory is mounted at `/workspace` inside the container. Changes made to tracked source files are therefore visible on the host and in Git.

If the container is already running and you only need another shell:

```bash
docker exec -it px4-gazebo-criticality bash
```

### Step 3 — Check the existing installation

Inside the container:

```bash
doctor
```

The doctor script checks ROS 2, Gazebo, Micro XRCE-DDS Agent, the ROS workspace, PX4 source/build output and GUI access.

If the checks show that PX4, the Agent and the workspace are present, continue to the build/run steps below. If a dependency is genuinely missing, inspect the corresponding setup script and `setup/versions.txt` before rerunning that individual setup step.

### Step 4 — Source the environment if needed

The container entrypoint sources `docker/env.sh` for each interactive shell. If you opened a shell where the environment is not loaded, run:

```bash
source /workspace/docker/env.sh
```

This sources ROS 2 Jazzy and the built workspace, activates the project virtual environment if present, sets project paths and defines convenience aliases.

### Step 5 — Build the ROS 2 workspace

After changing Python package code, configuration files, entry points or ROS package metadata, rebuild:

```bash
build
```

The alias runs `scripts/container/build.sh`, which builds `ros2_ws` using `colcon` and checks that `criticality_core` is discoverable.

For a clean rebuild only when necessary:

```bash
clean
build
```

`clean` removes `ros2_ws/build`, `ros2_ws/install` and `ros2_ws/log`. It does not delete PX4 source or the Micro XRCE-DDS Agent.

### Step 6 — Verify the package

```bash
source /workspace/ros2_ws/install/setup.bash
ros2 pkg list | grep criticality_core
ros2 pkg executables criticality_core
```

You should see the package and the console scripts registered in `setup.py`.

---

## Build after changing code

The source package is located at:

```text
/workspace/ros2_ws/src/criticality_core/
```

Typical development cycle:

1. Edit the relevant Python file, YAML configuration, launch file or package metadata on the host.
2. Rebuild inside the container:

   ```bash
   build
   ```

3. Source the workspace if the current shell needs the refreshed install environment:

   ```bash
   source /workspace/ros2_ws/install/setup.bash
   ```

4. Confirm the executable is available:

   ```bash
   ros2 pkg executables criticality_core
   ```

5. Run the relevant node or simulation workflow.

For a Python-only edit, the current build script still performs a normal `colcon build`. The package is not configured here with `--symlink-install`, so rebuild after source changes rather than assuming the installed copy has refreshed.

---

## Run a simulation

The following is the intended multi-terminal workflow based on the scripts and node entry points in the supplied repository. Keep each long-running process in its own terminal.

### Host terminal — open a container shell

```bash
cd ~/Desktop/Github/PX4-Gazebo-Criticality
./scripts/host/start_dev.sh
```

For additional terminals, open another host terminal and run:

```bash
cd ~/Desktop/Github/PX4-Gazebo-Criticality
docker exec -it px4-gazebo-criticality bash
```

### Container terminal 1 — start the Micro XRCE-DDS Agent

```bash
agent
```

This runs the configured UDP agent on port `8888`.

### Container terminal 2 — start PX4 SITL and Gazebo

```bash
sim
```

The `sim` alias runs:

```bash
cd /workspace/robotics/PX4-Autopilot
make px4_sitl gz_x500_mono_cam
```

Wait for PX4 and Gazebo to finish starting. In the PX4 shell, the existing project workflow may require:

```text
param set NAV_DLL_ACT 0
```

This changes the PX4 parameter for the current SITL session. Only apply it when required by the experiment you are running.

### Container terminal 3 — start the scenario runner

```bash
ros2 run criticality_core scenario_runner
```

The current `ScenarioRunner` loads `default_scenario.yaml`, validates it, creates a dataset session, initializes the event and navigation managers, and publishes navigation targets.

### Container terminal 4 — start the offboard controller

```bash
ros2 run criticality_core offboard_takeoff
```

This starts the offboard controller that sends PX4 offboard messages and consumes the navigation target topic.

### Container terminal 5 — start dataset logging

```bash
ros2 run criticality_core dataset_logger
```

The dataset logger joins the current dataset session and subscribes to the processed camera image, PX4 IMU, local-position and attitude topics.

### Optional — camera degradation node

The package exposes this executable:

```bash
ros2 run criticality_core camera_degradation_node
```

Use it when the camera processing path is part of the scenario being tested. Ensure the bridge and camera source are publishing the expected image topic.

### Check available executables

If a command is not found:

```bash
ros2 pkg executables criticality_core
```

Then check `setup.py`, rebuild the workspace and source the install setup file.

### Stop the simulation

Stop each running ROS/PX4 process with `Ctrl+C` in its own terminal. To stop the development container from the host:

```bash
./scripts/host/stop_dev.sh
```

---

## Scenario configuration

Scenario YAML files are stored in:

```text
ros2_ws/src/criticality_core/config/
```

Current files in the supplied repository:

- `default_scenario.yaml`
- `default_scenario_overlap.yaml`

The configuration is organized around:

```yaml
experiment:
  name: "experiment_name"
  random_seed: null
  max_duration: 180.0

navigation:
  mode: "fixed_waypoints"

events:
  - id: obstacle_001
    type: obstacle
    enabled: true
    severity: high
    trigger:
      x: 4.5
      y: 0.0
      z: -3.0
      radius: 0.75
    parameters:
      model_file: critical_box.sdf
      model_name: critical_box_001
      spawn:
        x: 5.0
        y: 0.0
        z: 0.5

logging:
  save_images: true
  save_imu: true
  save_groundtruth: true
  save_criticality_labels: true
```

The example above illustrates the current default obstacle configuration. Use the actual YAML file as the authoritative configuration.

### Trigger types present in source

- **Zone trigger:** Evaluates whether the vehicle position is inside a spherical region.
- **Time trigger:** Evaluates elapsed experiment time against a configured delay and optional duration.

The time trigger supports a delayed active interval. The default runner's configuration-loading behavior should be considered when testing a non-default YAML file; the existence of a second YAML file does not mean it is selected automatically.

### Editing a scenario safely

1. Back up the YAML file before changing it.
2. Keep event IDs unique within the scenario.
3. Confirm the event type is supported by the event factory.
4. Confirm the parameters match the selected event class.
5. Confirm the trigger fields match the trigger implementation.
6. Rebuild if package installation/configuration behavior requires it.
7. Run a short simulation and inspect logs and generated labels before running a longer experiment.

---

## Criticality events

The repository includes event classes for the following event categories.

| Event type | Implemented mechanism in the source | What to validate experimentally |
|---|---|---|
| Obstacle | Creates a Gazebo model through the entity-management path; fixed and relative placement logic exists in the source | Confirm spawn success, position, timing and vehicle response |
| GPS | Uses the PX4 failure-injection path | Confirm the intended PX4 message/failure state and correlate it with recorded GPS/navigation response |
| Sensor degradation | Supports camera processing and PX4 sensor failure-injection paths | Confirm the selected sensor path, event interval and measured sensor/image effect |
| Battery | Uses the battery controller and PX4 simulator battery parameters | Confirm parameter changes, battery telemetry and any resulting PX4 failsafe behavior |

### Event lifecycle

The event framework uses a lifecycle with activation, updates while active and exit/completion. The criticality logger records event metadata and selected telemetry at event start, then records the event offset when the event ends.

The label file is intended to associate event timing and context with the sensor/state streams. Treat event labels as annotations of the configured/invoked event lifecycle; do not assume every label proves a successful physical or estimator-level effect.

---

## Dataset generation

### Output location

The dataset path is configured in `criticality_core/config.py`. The sequence manager creates numbered sequence directories under the configured dataset root.

A typical sequence has this layout:

```text
sequence_xxxx/
├── mav0/
│   ├── cam0/
│   │   ├── data/
│   │   │   └── <image_timestamp>.png
│   │   └── data.csv
│   ├── imu0/
│   │   └── data.csv
│   └── state_groundtruth_estimate0/
│       └── data.csv
└── criticality_labels.csv
```

### Recorded streams

| Stream | Input | Output |
|---|---|---|
| Camera | Processed ROS `sensor_msgs/Image` topic `/criticality/camera/image` | PNG images and camera index CSV |
| IMU | PX4 `/fmu/out/sensor_combined` | Angular velocity and linear acceleration CSV |
| Vehicle state | PX4 local position and attitude topics | Position, velocity and quaternion state CSV |
| Criticality events | Event lifecycle and telemetry snapshot | `criticality_labels.csv` |

### Timestamp notes

- Camera image timestamps are taken from the image message header.
- PX4 IMU and vehicle-state messages contain PX4 timestamps in microseconds.
- The dataset logger also captures ROS simulation-clock time at message receipt and the CSV writer converts the relevant microsecond timestamps to nanoseconds.
- Ground-truth-style rows are anchored to the position timestamp and use the latest received attitude sample. Position and attitude are not guaranteed to be an exactly synchronized pair.
- The IMU and ground-truth logging timers are configured for 200 Hz and 50 Hz respectively, with duplicate-sample suppression. These timer rates are not a guarantee that every requested sample will be available or written.

### Inspect a generated sequence

On the host, inspect the configured dataset directory and confirm that a new sequence contains:

- `cam0/data/` image files
- `cam0/data.csv`
- `imu0/data.csv`
- `state_groundtruth_estimate0/data.csv`
- `criticality_labels.csv`

Check that timestamps are non-zero, files contain data rows, and event onset/offset values are plausible relative to the run. For scientific use, also verify clock consistency and event-to-sensor alignment.

---

## Useful development commands

Run these inside the development container unless otherwise stated.

| Command | Purpose |
|---|---|
| `doctor` | Check the installed runtime and workspace |
| `build` | Build the ROS 2 workspace |
| `clean` | Remove ROS workspace build/install/log artifacts |
| `sim` | Start PX4 SITL with Gazebo x500 monocular camera |
| `agent` | Start Micro XRCE-DDS Agent on UDP port 8888 |
| `ws` | Change directory to `/workspace` |
| `px4` | Change directory to the PX4 source tree |
| `rosws` | Change directory to `/workspace/ros2_ws` |
| `setup` | Change directory to `/workspace/setup` |

Useful ROS checks:

```bash
ros2 node list
ros2 topic list
ros2 topic info /navigation/target
ros2 topic echo /navigation/target
ros2 pkg executables criticality_core
```

Useful Git checks on the host:

```bash
git status
git diff
git diff --stat
git log --oneline -5
```

---

## Troubleshooting

### `doctor` reports that the ROS workspace is not built

Inside the container:

```bash
source /opt/ros/jazzy/setup.bash
build
```

### ROS cannot find `criticality_core`

```bash
cd /workspace/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
ros2 pkg list | grep criticality_core
```

### PX4 message package/build artifacts are stale

First inspect the actual `colcon` error. If it specifically indicates stale `px4_msgs` build/install artifacts, remove only those generated directories and rebuild:

```bash
cd /workspace/ros2_ws
rm -rf build/px4_msgs install/px4_msgs
colcon build
source install/setup.bash
```

Do not delete source directories under `src/`.

### Gazebo GUI does not open

On the host, confirm that a graphical session is active and `DISPLAY` is set:

```bash
echo "$DISPLAY"
xhost
```

Restart the development container using the supplied host script. The current Compose configuration uses host networking and X11 socket forwarding; Wayland-only environments may need additional display configuration.

### Micro XRCE-DDS Agent cannot connect

Check that the agent is running:

```bash
pgrep -af MicroXRCEAgent
```

Confirm the PX4 uXRCE-DDS client is configured to use the same transport and UDP port (the supplied convenience alias uses port `8888`).

### No PX4 topics appear in ROS 2

Check, in order:

1. PX4 SITL is running.
2. Micro XRCE-DDS Agent is running.
3. PX4 and ROS 2 use compatible message definitions.
4. `px4_msgs` and `px4_ros_com` are at the commits pinned in `setup/versions.txt`.
5. The ROS 2 environment is sourced.

Then inspect:

```bash
ros2 topic list | grep fmu
```

### Dataset files are missing or empty

Check that:

- `ScenarioRunner` created the dataset session.
- `DatasetLogger` is running and joined that same session.
- The camera processing/bridge path is publishing `/criticality/camera/image`.
- PX4 IMU, position and attitude topics are publishing.
- The logger has received valid non-zero timestamps.

---

## Research and real-world relevance

Although the experiments run in simulation, the project addresses problems that arise in real autonomous UAV operation.

### 1. Robustness evaluation for autonomous navigation

A navigation system can be evaluated under controlled obstacle placement, sensor outages and degraded observations. Simulation makes it possible to repeat a condition with known parameters and compare system behavior across runs.

### 2. Safety-critical dataset generation

Real-world collection of rare failures can be expensive, difficult to reproduce and potentially unsafe. A simulator can create controlled examples of unusual or adverse conditions while recording the state and event context needed for later analysis.

### 3. Perception under degraded sensing

Camera degradation can be used to study how visual perception or visual navigation responds to noise, blur, brightness changes or other image transformations. The current repository includes camera image processing components; further work can add systematic parameter sweeps and evaluation metrics.

### 4. Sensor-failure and navigation resilience research

GPS and IMU failure paths can support research into localization robustness, sensor consistency checks and fault-aware navigation. Each experiment must verify that the intended failure was actually applied and that the observed measurements changed as expected.

### 5. Criticality prediction and machine learning

The long-term dataset objective is to associate camera, IMU and vehicle-state sequences with event intervals and severity labels. Such data could support future work on:

- Criticality or risk prediction from onboard observations.
- Learning-based anomaly and fault detection.
- Robustness evaluation of perception and navigation models.
- Reinforcement-learning environments with controlled adverse events.
- Scenario coverage analysis and curriculum generation.

These are research applications enabled by the intended dataset direction; trained prediction or reinforcement-learning models are not included in the current repository snapshot.

### 6. Sim-to-real research

A carefully designed simulator can provide controlled pre-deployment testing. However, simulation results do not automatically transfer to physical UAVs. Real-world deployment requires model validation, sensor calibration, domain-gap analysis, hardware-in-the-loop or flight testing, and appropriate safety procedures.

---

## Limitations and next development steps

The following items are useful priorities for continued development. They should be treated as roadmap items unless verified in the source and experiments.

1. **Scenario selection:** Add a clean command-line or launch argument to select a YAML scenario instead of relying on the current hard-coded default filename.
2. **Trigger expansion:** Extend beyond the current zone and time triggers with waypoint, distance, target-relative, mission-state, random and conditional triggers.
3. **Scenario reproducibility:** Apply and record random seeds consistently; verify that every randomized component uses the configured seed.
4. **Duration enforcement:** Ensure configured experiment maximum duration is enforced by the runtime.
5. **Event validation:** Add event-aligned tests and run artifacts proving the effect of GPS, IMU and battery injections.
6. **Moving targets:** Complete and validate moving-target navigation workflows; implement random-target navigation (the supplied module is currently empty).
7. **Dataset synchronization:** Define and test a consistent timestamp policy across camera, IMU, position, attitude and event labels.
8. **Dataset metadata:** Add calibration/configuration metadata and validation tools before claiming full EuRoC compatibility.
9. **Batch generation:** Add automated scenario sampling, seed management and batch-run orchestration.
10. **Evaluation pipeline:** Add metrics and scripts for dataset integrity, event coverage and robustness evaluation.
11. **Learning integration:** Consider PPO, SAC or TD3 only after a stable simulation interface and repeatable dataset/scenario evaluation pipeline are established.
12. **Packaging and tests:** Expand automated tests and verify declared ROS package dependencies and setup metadata against a clean build.

---

## Contributing and reproducibility

Before committing changes:

1. Keep generated dependencies and experiment output out of Git.
2. Update `setup/versions.txt` deliberately when changing pinned external revisions.
3. Keep scenario configuration and code behavior consistent.
4. Add or update tests for changes to triggers, event lifecycles, coordinate conversion and logging.
5. Run the workspace build and relevant tests inside the supported container.
6. Record the scenario configuration, software revisions and relevant run metadata for research results.

A typical test command inside the container is:

```bash
cd /workspace/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
colcon test --packages-select criticality_core
colcon test-result --verbose
```

The supplied tests cover selected areas only; a passing test suite is not a complete system-level safety validation.

---

## Push your changes to GitHub

Run these commands **on the Ubuntu host**, from the cloned repository root, not from inside the Docker container.

### 1. Review what will be committed

```bash
cd ~/Desktop/Github/PX4-Gazebo-Criticality

git status
git diff -- README.md
```

### 2. Replace the README

Save this document as `README.md` in the repository root, replacing the old README.

### 3. Stage and review

```bash
git add README.md
git status
git diff --cached
```

If you have also changed source files and intend to publish them, stage those files deliberately. Do not blindly add generated datasets, build products, virtual environments or downloaded PX4/Agent source.

To stage all intended tracked changes after checking `.gitignore`:

```bash
git add -A
git status
git diff --cached --stat
```

### 4. Commit

```bash
git commit -m "docs: update project README and development workflow"
```

### 5. Push the current branch

```bash
git push origin "$(git branch --show-current)"
```

If this is the first push of a new local branch and Git reports that no upstream is configured:

```bash
git push -u origin "$(git branch --show-current)"
```

If authentication is requested, complete it using your configured Git credential manager or SSH key.

---

## License

The supplied repository README identifies the project as intended for research and educational use but does not specify a formal open-source license. Before accepting external contributions or redistributing the project, add an explicit license file and confirm the licensing terms of all included and externally downloaded components.
