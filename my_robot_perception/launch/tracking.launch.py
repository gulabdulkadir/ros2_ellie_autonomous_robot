import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    """
    # 1. Ortam değişkenini otomatik ayarla (export TURTLEBOT3_MODEL=waffle_pi) yazıyoduk onun yerine.
    set_tb3_model = SetEnvironmentVariable(
        name="TURTLEBOT3_MODEL",
        value="waffle_pi"
    )
    """

    # 2. TurtleBot3 Gazebob launch dosyasının yolunu bul ve dahil et.
    ellie_description_dir = get_package_share_directory('ellie_description')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ellie_description_dir, 'launch', 'gazebo.launch.py')
        )
    )



    pkg_perception_dir = get_package_share_directory('my_robot_perception')
    params_file = os.path.join(pkg_perception_dir, 'config', 'params.yaml')

    # 3. Rviz dosyasinin yerini bul ve dahil et.
    rviz_config_dir = os.path.join(pkg_perception_dir, 'rviz', 'tracking.rviz')


    rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    arguments=['-d', rviz_config_dir],
    parameters=[{'use_sim_time': True}],
    output='screen'
    )
    perception_node = Node(
    package='my_robot_perception',
    executable='yolo_baslat',
    output='screen'
    )
    control_node = Node(
    package='my_robot_perception',
    executable='motor_baslat',
    parameters=[params_file],
    output='screen'
    )
    return LaunchDescription([
#        set_tb3_model,
        gazebo_launch,
        perception_node,
        control_node,
        rviz_node,
    ])