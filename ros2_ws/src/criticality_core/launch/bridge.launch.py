from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"
        ],
        output="screen",
    )

    return LaunchDescription([
        clock_bridge,
    ])
