#!/usr/bin/env python3

from pathlib import Path

from criticality_core.config import DATASETS_DIR


class SequenceManager:
    """
    Creates and manages one EuRoC sequence directory.

    Example:

    datasets/
        sequence_0001/
            mav0/
                cam0/
                    data/
                imu0/
                state_groundtruth_estimate0/
    """

    def __init__(
        self,
        sequence_dir=None,
    ):

        # --------------------------------------------------
        # Dataset Root
        # --------------------------------------------------

        self.dataset_root = DATASETS_DIR

        self.dataset_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # Sequence
        # --------------------------------------------------

        if sequence_dir is None:

            self.sequence_name = (
                self._next_sequence_name()
            )

            self.sequence_dir = (
                self.dataset_root
                / self.sequence_name
            )

        else:

            self.sequence_dir = Path(
                sequence_dir
            )

            self.sequence_name = (
                self.sequence_dir.name
            )

        # --------------------------------------------------
        # EuRoC Folder Structure
        # --------------------------------------------------

        self.mav0_dir = (
            self.sequence_dir
            / "mav0"
        )

        self.cam0_dir = (
            self.mav0_dir
            / "cam0"
        )

        self.cam0_data_dir = (
            self.cam0_dir
            / "data"
        )

        self.imu_dir = (
            self.mav0_dir
            / "imu0"
        )

        self.gt_dir = (
            self.mav0_dir
            / "state_groundtruth_estimate0"
        )

        # --------------------------------------------------
        # Create Directories
        # --------------------------------------------------

        self.cam0_data_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.imu_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.gt_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # CSV Paths
        # --------------------------------------------------

        self.cam_csv = (
            self.cam0_dir
            / "data.csv"
        )

        self.imu_csv = (
            self.imu_dir
            / "data.csv"
        )

        self.gt_csv = (
            self.gt_dir
            / "data.csv"
        )

        self.labels_csv = (
            self.sequence_dir
            / "criticality_labels.csv"
        )

    # ==================================================
    # Private Helpers
    # ==================================================

    def _next_sequence_name(self):

        existing = []

        for path in self.dataset_root.iterdir():

            if (
                path.is_dir()
                and path.name.startswith(
                    "sequence_"
                )
            ):

                try:

                    number = int(
                        path.name.split("_")[1]
                    )

                    existing.append(number)

                except ValueError:

                    pass

        next_number = (
            max(existing) + 1
            if existing
            else 1
        )

        return (
            f"sequence_{next_number:04d}"
        )
        
    # ==================================================
    # String Representation
    # ==================================================

    def __str__(self):

        return str(self.sequence_dir)
