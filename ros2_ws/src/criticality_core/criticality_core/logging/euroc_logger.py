
#!/usr/bin/env python3

import csv

import cv2


class EuRoCLogger:
    """
    Creates and manages a EuRoC-compatible dataset sequence.

    Stage 1:
        - Creates CSV files.
        - Writes headers.
        - Keeps files open for logging.
    """

    def __init__(
        self,
        sequence_manager,
    ):

        self.sequence_manager = sequence_manager
        self.sequence_dir = sequence_manager.sequence_dir

        # ------------------------------------------
        # Camera CSV
        # ------------------------------------------

        self.cam_file = open(
            self.sequence_manager.cam_csv,
            "w",
            newline="",
        )

        self.cam_writer = csv.writer(
            self.cam_file
        )

        self.cam_writer.writerow(
            [
                "#timestamp [ns]",
                "filename",
            ]
        )

        # ------------------------------------------
        # IMU CSV
        # ------------------------------------------

        self.imu_file = open(
            self.sequence_manager.imu_csv,
            "w",
            newline="",
        )

        self.imu_writer = csv.writer(
            self.imu_file
        )

        self.imu_writer.writerow(
            [
                "#timestamp [ns]",
                "#simulation_timestamp [ns]",
                "w_RS_S_x [rad s^-1]",
                "w_RS_S_y [rad s^-1]",
                "w_RS_S_z [rad s^-1]",
                "a_RS_S_x [m s^-2]",
                "a_RS_S_y [m s^-2]",
                "a_RS_S_z [m s^-2]",
            ]
        )

        # ------------------------------------------
        # Ground Truth CSV
        # ------------------------------------------

        self.gt_file = open(
            self.sequence_manager.gt_csv,
            "w",
            newline="",
        )

        self.gt_writer = csv.writer(
            self.gt_file
        )

        self.gt_writer.writerow(
            [
                "#timestamp",
                "#simulation_timestamp [ns]",
                "p_RS_R_x [m]",
                "p_RS_R_y [m]",
                "p_RS_R_z [m]",
                "q_RS_w []",
                "q_RS_x []",
                "q_RS_y []",
                "q_RS_z []",
                "v_RS_R_x [m s^-1]",
                "v_RS_R_y [m s^-1]",
                "v_RS_R_z [m s^-1]",
            ]
        )

    # ==================================================
    # IMU Logging
    # ==================================================

    def log_imu(
        self,
        timestamp_us: int,
        simulation_timestamp_us: int,
        gyro: list,
        accel: list,
    ):
        """
        Writes one IMU measurement to the EuRoC dataset.

        Parameters
        ----------
        timestamp_us
            Original PX4 timestamp in microseconds.

        simulation_timestamp_us
            Corresponding Gazebo simulation timestamp in microseconds.

        gyro
            Angular velocity [gx, gy, gz] in rad/s.

        accel
            Linear acceleration [ax, ay, az] in m/s².
        """

        if len(gyro) != 3:
            raise ValueError(
                "gyro must contain exactly three values."
            )

        if len(accel) != 3:
            raise ValueError(
                "accel must contain exactly three values."
            )

        # Convert both timestamps from microseconds to nanoseconds.
        timestamp_ns = timestamp_us * 1000
        simulation_timestamp_ns = simulation_timestamp_us * 1000

        self.imu_writer.writerow(
            [
                timestamp_ns,
                simulation_timestamp_ns,
                gyro[0],
                gyro[1],
                gyro[2],
                accel[0],
                accel[1],
                accel[2],
            ]
        )

        self.imu_file.flush()

    # ==================================================
    # Ground Truth Logging
    # ==================================================

    def log_groundtruth(
        self,
        timestamp_us: int,
        simulation_timestamp_us: int,
        position: list,
        orientation: list,
        velocity: list,
    ):
        """
        Writes one ground-truth measurement to the EuRoC dataset.

        Parameters
        ----------
        timestamp_us
            Original PX4 timestamp in microseconds.

        simulation_timestamp_us
            Corresponding Gazebo simulation timestamp in microseconds.

        position
            Vehicle position [x, y, z] in meters.

        orientation
            Vehicle orientation quaternion [qw, qx, qy, qz].

        velocity
            Vehicle linear velocity [vx, vy, vz] in m/s.
        """

        if len(position) != 3:
            raise ValueError(
                "position must contain exactly three values."
            )

        if len(orientation) != 4:
            raise ValueError(
                "orientation must contain exactly four values."
            )

        if len(velocity) != 3:
            raise ValueError(
                "velocity must contain exactly three values."
            )

        # Convert both timestamps from microseconds to nanoseconds.
        timestamp_ns = timestamp_us * 1000
        simulation_timestamp_ns = simulation_timestamp_us * 1000

        self.gt_writer.writerow(
            [
                timestamp_ns,
                simulation_timestamp_ns,
                position[0],
                position[1],
                position[2],
                orientation[0],
                orientation[1],
                orientation[2],
                orientation[3],
                velocity[0],
                velocity[1],
                velocity[2],
            ]
        )

        self.gt_file.flush()

    # ==================================================
    # Camera Logging
    # ==================================================

    def log_camera(
        self,
        timestamp_ns: int,
        image,
    ):
        """
        Writes one camera image to the EuRoC dataset.

        Parameters
        ----------
        timestamp_ns
            Image timestamp in nanoseconds.

        image
            OpenCV image (numpy array).
        """

        filename = f"{timestamp_ns}.png"

        image_path = (
            self.sequence_manager.cam0_data_dir
            / filename
        )

        success = cv2.imwrite(
            str(image_path),
            image,
        )

        if not success:
            raise RuntimeError(
                f"Failed to save image: {image_path}"
            )

        self.cam_writer.writerow(
            [
                timestamp_ns,
                filename,
            ]
        )

        self.cam_file.flush()

    # ==================================================
    # Shutdown
    # ==================================================

    def close(self):

        if not self.cam_file.closed:
            self.cam_file.close()

        if not self.imu_file.closed:
            self.imu_file.close()

        if not self.gt_file.closed:
            self.gt_file.close()

