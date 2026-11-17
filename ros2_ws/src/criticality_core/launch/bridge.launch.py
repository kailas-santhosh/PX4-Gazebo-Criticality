from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="clock_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"
        ],
        output="screen",
    )

    camera_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="camera_bridge",
        arguments=[
            "/world/default/model/x500_mono_cam_0/link/camera_link/sensor/imager/image@sensor_msgs/msg/Image[gz.msgs.Image"
        ],
        output="screen",
    )

    return LaunchDescription([
        clock_bridge,
        camera_bridge,
    ])
