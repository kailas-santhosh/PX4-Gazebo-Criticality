import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy,
)

from px4_msgs.msg import VehicleGlobalPosition


class GPSMonitor(Node):

    def __init__(self):
        super().__init__("gps_monitor")

        # PX4 commonly publishes sensor and position topics
        # using Best Effort reliability.
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.gps_sub = self.create_subscription(
            VehicleGlobalPosition,
            "/fmu/out/vehicle_global_position",
            self.callback,
            qos_profile,
        )

        self.get_logger().info(
            "Waiting for global position data..."
        )

    def callback(self, msg):
        self.get_logger().info(
            f"\n"
            f"Latitude       : {msg.lat:.7f}\n"
            f"Longitude      : {msg.lon:.7f}\n"
            f"Altitude       : {msg.alt:.2f} m\n"
            f"Lat/Lon valid  : {msg.lat_lon_valid}\n"
            f"Altitude valid : {msg.alt_valid}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = GPSMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
