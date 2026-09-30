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
            "hello_node = criticality_core.hello_node:main",
            "offboard_takeoff = criticality_core.offboard_takeoff:main",
            "spawn_obstacle = criticality_core.spawn_obstacle:main",
        ],
    },
)
