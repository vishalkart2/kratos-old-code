from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
	return LaunchDescription([
	Node(
		package='drive_controls',
		namespace='',
		executable='drive.py',
		name='drove'
	)
	])
