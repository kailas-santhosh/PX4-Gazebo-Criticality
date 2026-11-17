#!/usr/bin/env python3

from criticality_core.logging.sequence_manager import SequenceManager
from criticality_core.logging.euroc_logger import EuRoCLogger
import numpy as np


def main():

    print("\nCreating sequence...")

    sequence_manager = SequenceManager()

    print(f"Sequence directory:")
    print(f"  {sequence_manager.sequence_dir}")

    logger = EuRoCLogger(
        sequence_manager=sequence_manager,
    )

    print("\nLogging IMU sample...")

    logger.log_imu(
        timestamp_us=100,
        gyro=[1.0, 2.0, 3.0],
        accel=[4.0, 5.0, 6.0],
    )

    print("Logging Ground Truth sample...")

    logger.log_groundtruth(
        timestamp_us=200,
        position=[10.0, 20.0, 30.0],
        orientation=[1.0, 0.0, 0.0, 0.0],
        velocity=[7.0, 8.0, 9.0],
    )

    print("Logging Camera sample...")

    image = np.full(
        (480, 640, 3),
        255,
        dtype=np.uint8,
    )

    logger.log_camera(
        timestamp_ns=300000,
        image=image,
    )

    logger.close()

    print("\nTest completed successfully.")

    print("\nGenerated files:")

    print(f"  {sequence_manager.cam_csv}")
    print(f"  {sequence_manager.imu_csv}")
    print(f"  {sequence_manager.gt_csv}")
    print(f"  {sequence_manager.cam0_data_dir}")

if __name__ == "__main__":
    main()
