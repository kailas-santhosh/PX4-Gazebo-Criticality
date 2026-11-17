#!/usr/bin/env python3

import json

from std_msgs.msg import String


class CameraController:
    """
    High-level interface for controlling camera degradation.

    This class hides all ROS communication from the event system.

    SensorEvent simply calls methods like:

        enable_gaussian_noise(...)
        enable_motion_blur(...)
        enable_blur(...)
        disable()

    without knowing how the CameraDegradationNode
    receives those commands.
    """

    # --------------------------------------------------

    def __init__(self, node):

        self.node = node

        self.publisher = self.node.create_publisher(
            String,
            "/criticality/camera/command",
            10,
        )

    # --------------------------------------------------
    # Internal Helper
    # --------------------------------------------------

    def _publish_command(
        self,
        mode,
        level,
    ):

        msg = String()

        msg.data = json.dumps(
            {
                "mode": mode,
                "level": float(level),
            }
        )

        self.publisher.publish(msg)

        self.node.get_logger().info(
            f"Camera command published: "
            f"{mode} ({level:.2f})"
        )

    # --------------------------------------------------
    # Gaussian Noise
    # --------------------------------------------------

    def enable_gaussian_noise(
        self,
        level,
    ):

        self._publish_command(
            "gaussian_noise",
            level,
        )

    # --------------------------------------------------
    # Motion Blur
    # --------------------------------------------------

    def enable_motion_blur(
        self,
        level,
    ):

        self._publish_command(
            "motion_blur",
            level,
        )

    # --------------------------------------------------
    # Gaussian Blur
    # --------------------------------------------------

    def enable_blur(
        self,
        level,
    ):

        self._publish_command(
            "blur",
            level,
        )

    # --------------------------------------------------
    # Frame Drop
    # --------------------------------------------------

    def enable_frame_drop(
        self,
        probability,
    ):

        self._publish_command(
            "frame_drop",
            probability,
        )

    # --------------------------------------------------
    # Brightness
    # --------------------------------------------------

    def enable_brightness(
        self,
        factor,
    ):

        self._publish_command(
            "brightness",
            factor,
        )

    # --------------------------------------------------
    # Contrast
    # --------------------------------------------------

    def enable_contrast(
        self,
        factor,
    ):

        self._publish_command(
            "contrast",
            factor,
        )

    # --------------------------------------------------
    # Salt & Pepper
    # --------------------------------------------------

    def enable_salt_pepper(
        self,
        probability,
    ):

        self._publish_command(
            "salt_pepper",
            probability,
        )

    # --------------------------------------------------
    # Disable
    # --------------------------------------------------

    def disable(self):

        self._publish_command(
            "restore",
            0.0,
        )
