from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='arm_controls',
            executable='arm_mapping',
            name='arm_mapping',
            output='screen'
        )
    ])
