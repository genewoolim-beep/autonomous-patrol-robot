"""
mission.launch.py
================
미션 매니저 노드를 네임스페이스와 함께 실행한다.

사용:
  ros2 launch mission_manager_pkg mission.launch.py namespace:=robot4

SLAM / Nav2 / 하드웨어 / YOLO / explore_lite 는 이미 별도로 떠 있다고 가정한다.
이 launch는 우리가 만든 미션 매니저 '하나'만 띄운다.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')

    declare_ns = DeclareLaunchArgument(
        'namespace', default_value='robot4',
        description='로봇 네임스페이스')

    mission_manager = Node(
        package='mission_manager_pkg',
        executable='mission_manager',
        name='mission_manager',
        namespace=namespace,
        output='screen',
        parameters=[{'tick_hz': 10.0}],
    )

    return LaunchDescription([
        declare_ns,
        mission_manager,
    ])
