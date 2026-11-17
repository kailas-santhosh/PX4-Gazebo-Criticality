
#!/usr/bin/env python3

import json

import cv2
import numpy as np

import rclpy

from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String

from cv_bridge import CvBridge

from criticality_core.sensors.image_degradations import (
    add_gaussian_noise,
    adjust_brightness,
    adjust_contrast,
    add_salt_pepper_noise,
    drop_frame,
    identity,
)


class CameraDegradationNode(Node):

    def __init__(self):

        super().__init__("camera_degradation_node")

        # --------------------------------------------------
        # Camera Topics
        # --------------------------------------------------

        self.input_topic = (
            "/world/default/model/x500_mono_cam_0/link/camera_link/sensor/imager/image"
        )

        self.output_topic = (
            "/criticality/camera/image"
        )

        self.command_topic = (
            "/criticality/camera/command"
        )

        # --------------------------------------------------
        # CV Bridge
        # --------------------------------------------------

        self.bridge = CvBridge()

        # --------------------------------------------------
        # Degradation State
        # --------------------------------------------------

        self.enabled = False
        self.mode = "none"
        self.level = 0.0

        # --------------------------------------------------
        # Image Subscriber
        # --------------------------------------------------

        self.subscription = self.create_subscription(
            Image,
            self.input_topic,
            self.image_callback,
            10,
        )

        # --------------------------------------------------
        # Command Subscriber
        # --------------------------------------------------

        self.command_subscription = self.create_subscription(
            String,
            self.command_topic,
            self.command_callback,
            10,
        )

        # --------------------------------------------------
        # Image Publisher
        # --------------------------------------------------

        self.publisher = self.create_publisher(
            Image,
            self.output_topic,
            10,
        )

        self.get_logger().info(
            "Camera Degradation Node initialized."
        )

    # --------------------------------------------------
    # Command Callback
    # --------------------------------------------------

    def command_callback(self, msg):

        try:

            command = json.loads(msg.data)

            mode = command.get("mode", "none")
            level = float(command.get("level", 0.0))

            if mode == "restore":

                self.enabled = False
                self.mode = "none"
                self.level = 0.0

            else:

                self.enabled = mode != "none"
                self.mode = mode
                self.level = level

            self.get_logger().info(
                f"Camera mode={self.mode}, "
                f"level={self.level:.2f}, "
                f"enabled={self.enabled}"
            )

        except Exception as e:

            self.get_logger().error(str(e))

    # --------------------------------------------------
    # Image Callback
    # --------------------------------------------------

    def image_callback(self, msg):

        # --------------------------------------------------
        # Convert ROS image to OpenCV image
        # --------------------------------------------------

        image = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding="bgr8",
        )

        # --------------------------------------------------
        # Apply Selected Degradation
        # --------------------------------------------------

        if not self.enabled:

            image = identity(image)

        elif self.mode == "gaussian_noise":

            image = add_gaussian_noise(
                image,
                self.level,
            )

        elif self.mode == "motion_blur":

            k = max(
                3,
                int(self.level * 25),
            )

            if k % 2 == 0:
                k += 1

            kernel = np.zeros(
                (k, k),
                dtype=np.float32,
            )

            kernel[k // 2, :] = 1.0 / k

            image = cv2.filter2D(
                image,
                -1,
                kernel,
            )

        # --------------------------------------------------
        # Blur
        # --------------------------------------------------

        elif self.mode == "blur":

            k = max(
                3,
                int(self.level * 15),
            )

            if k % 2 == 0:
                k += 1

            image = cv2.GaussianBlur(
                image,
                (k, k),
                0,
            )

        elif self.mode == "brightness":

            image = adjust_brightness(
                image,
                self.level,
            )

        elif self.mode == "contrast":

            image = adjust_contrast(
                image,
                self.level,
            )

        elif self.mode == "salt_pepper":

            image = add_salt_pepper_noise(
                image,
                probability=self.level,
            )

        elif self.mode == "frame_drop":

            image = drop_frame(image)

            if image is None:
                return

        else:

            image = identity(image)

        # --------------------------------------------------
        # Convert OpenCV -> ROS
        # --------------------------------------------------

        output = self.bridge.cv2_to_imgmsg(
            image,
            encoding="bgr8",
        )

        output.header = msg.header

        self.publisher.publish(output)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    rclpy.init()

    node = CameraDegradationNode()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":

    main()

