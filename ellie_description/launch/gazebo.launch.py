import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('ellie_description')
    xacro_file = os.path.join(pkg_path, 'urdf', 'ellie.urdf.xacro')

    # Xacro dosyasını bellekte derleyip saf URDF metnine çevir.
    robot_desc = xacro.process_file(xacro_file).toxml()

    # 1. Robot tanımını ve TF dönüşümlerini sim. zamanıyla yayınlar.
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # 2. gazebo_ros paketinin standart boş dünya launch dosyasını çağırır
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ])
    )

    # 3. /robot_description konusundaki modeli okuyup Gazebo sahnesine yerleştirir
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'ellie'
        ],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        gazebo,
        spawn_entity_node
    ])