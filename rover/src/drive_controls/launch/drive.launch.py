from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    drive_node = Node(
        package='drive_controls',
        executable='drive.py',
        name='drive',
        output='screen'
    )

    micro_ros_agent = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        arguments=['serial', '--dev', '/dev/ttyUSB0'],
        output='screen'
    )

    return LaunchDescription([
        drive_node,
        micro_ros_agent
    ])
