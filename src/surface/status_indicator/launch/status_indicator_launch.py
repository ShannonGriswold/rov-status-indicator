import os
from pathlib import Path
from ament_index_python import get_package_share_directory
from launch.launch_description import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions.launch_configuration import LaunchConfiguration




def generate_launch_description() -> LaunchDescription:
    status_indicator = Node(
        package='status_indicator',
        executable='status_indicator',
        name='status_indicator',
        exec_name='status_indicator',
        emulate_tty=True,
        output='screen',
        parameters=[
            {'status-simulation': LaunchConfiguration('status-simulation', default=False)}
        ],
    )

    bridge = Node(
        package='status_indicator',
        executable='bridge',
        emulate_tty=True,
        output='screen',
        parameters=[
            {'status-simulation': LaunchConfiguration('status-simulation', default=False)}
        ],
    )

    return LaunchDescription([status_indicator, bridge])
