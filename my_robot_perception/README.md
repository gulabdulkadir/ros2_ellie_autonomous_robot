# ROS 2 Visual Target Tracking (my_robot_perception)

Autonomous visual perception and target tracking pipeline built and simulated on **The Construct (theconstruct.ai)** cloud robotics environment using **ROS 2 Humble**, **OpenCV (`cv_bridge`)**, and **Gazebo** with a TurtleBot3 (`waffle_pi`) model.

## Architecture

[/camera/image_raw] --> (yolo_detection_node) --> [/yolo_detections] --> (motor_control_node) --> [/cmd_vel]

- yolo_node.py (yolo_detection_node): Subscribes to raw RGB camera frames (sensor_msgs/Image), converts them via cv_bridge, segments the target object using OpenCV thresholding and contour detection, and publishes horizontal pixel offset and proximity status.
- motor_node.py (motor_control_node): Subscribes to /yolo_detections, computes angular velocity using a Proportional Controller (w_z = -Kp * offset_x) following ROS 2 REP-103 right-hand rule conventions, and publishes geometry_msgs/Twist commands to /cmd_vel.

## Environment & Prerequisites

- Platform: The Construct (theconstruct.ai) ROS 2 Humble Workspace
- Simulator: Gazebo (TurtleBot3 waffle_pi)
- Dependencies: rclpy, sensor_msgs, std_msgs, geometry_msgs, cv_bridge, opencv-python, numpy<2

## Build & Run

1. Build the package:
   cd ~/ros2_ws
   colcon build --packages-select my_robot_perception
   source install/setup.bash

2. Run in separate terminals:
   - Terminal 1 (Gazebo): export TURTLEBOT3_MODEL=waffle_pi && ros2 launch turtlebot3_gazebo empty_world.launch.py
   - Terminal 2 (Perception): ros2 run my_robot_perception yolo_baslat
   - Terminal 3 (Control): ros2 run my_robot_perception motor_baslat
