from launch import LaunchDescription
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    package_dir = get_package_share_directory("criticality_core")

    world = os.path.join(
        package_dir,
        "worlds",
        "empty.sdf"
    )

    gazebo = ExecuteProcess(
        cmd=["gz", "sim", world],
        output="screen"
    )

    return LaunchDescription([
        gazebo
    ])
