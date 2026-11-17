from setuptools import find_packages, setup
from glob import glob

package_name = 'criticality_core'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/criticality_core"],
        ),

        (
            "share/criticality_core",
            ["package.xml"],
        ),

        (
            "share/criticality_core/launch",
            glob("launch/*.py"),
        ),

        (
            "share/criticality_core/worlds",
            glob("worlds/*.sdf"),
        ),

        (
            "share/criticality_core/config",
            glob("config/*.yaml"),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        "console_scripts": [
            "hello_node = criticality_core.utilities.hello_node:main",
            "offboard_takeoff = criticality_core.controllers.offboard_takeoff:main",
            "spawn_model = criticality_core.utilities.spawn_model:main",
            "gps_monitor = criticality_core.controllers.gps_monitor:main",
            "remove_model = criticality_core.utilities.remove_model:main",
            "move_model = criticality_core.utilities.move_model:main",
            "obstacle_demo = criticality_core.scenarios.obstacle_demo:main",
            "scenario_runner = criticality_core.scenarios.scenario_runner:main",
            "camera_degradation_node = criticality_core.sensors.camera_degradation_node:main",
            "dataset_logger = criticality_core.logging.dataset_logger:main",
            "moving_target_simulator = criticality_core.utilities.moving_target_simulator:main",
        ],
    },
)
