# Ellie — ROS 2 Autonomous Mobile Robot

A modular Xacro differential-drive robot model (`ellie`) and a multi-node perception-control pipeline built with ROS 2 Humble and Gazebo Classic. The system combines camera-based target tracking with 2D LiDAR obstacle avoidance.

## Repository Structure

```text
src/
 ellie_description/          # Modular URDF/Xacro robot model and Gazebo simulation setup
   ├── launch/
   │   └── gazebo.launch.py
   └── urdf/
       ├── ellie.urdf.xacro
       ├── common_properties.xacro
       ├── ellie_gazebo.xacro
       ├── lidar.xacro
       └── camera.xacro
 my_robot_interfaces/        # Custom ROS 2 message definitions
   └── msg/
       └── TargetInfo.msg
 my_robot_perception/        # Perception, control, and launch files
    ├── config/
    │   └── params.yaml
    ├── launch/
    │   └── tracking.launch.py
    ├── my_robot_perception/
    │   ├── yolo_node.py
    │   └── motor_node.py
    └── rviz/
        └── tracking.rviz
```

## Packages Overview

* **`ellie_description`**: Defines a differential-drive robot (`0.4m x 0.3m x 0.1m` chassis, two rear drive wheels, and a front caster) using modular Xacro files. Includes Gazebo plugins for differential drive (`/cmd_vel`, `/odom`), a 360° 2D LiDAR (`/scan`, `0.15m–10.0m` range), and an RGB camera (`/camera/image_raw`) with a REP-103 `camera_link_optical` frame.
* **`my_robot_interfaces`**: Defines the `TargetInfo` message (`string status`, `float64 offset_x`) used to pass detection states (`HEDEF_TAKIP`, `HEDEF_COK_YAKIN`, `HEDEF_YOK`) and horizontal pixel error between nodes.
* **`my_robot_perception`**:
  * **`yolo_node.py` (`yolo_baslat`)**: Subscribes to `/camera/image_raw`, detects target contours via OpenCV thresholding, calculates the horizontal offset from the image center, and publishes `TargetInfo` messages to `/yolo_detections`.
  * **`motor_node.py` (`motor_baslat`)**: Subscribes to `/yolo_detections` and `/scan` (`qos_profile_sensor_data`), computes angular velocity using a P-controller, enforces a front-cone (`ranges[160:200]`) LiDAR safety stop, and publishes velocity commands to `/cmd_vel`.

## Prerequisites

* ROS 2 Humble
* Gazebo Classic (`gazebo_ros_pkgs`)
* `xacro`, `cv_bridge`, `opencv-python`
* `numpy<2` (required for compatibility with ROS 2 Humble `cv_bridge`)

## Build & Run

```bash
cd ~/ros2_ws
colcon build --packages-select ellie_description my_robot_interfaces my_robot_perception
source install/setup.bash
ros2 launch my_robot_perception tracking.launch.py
```

## Parameters (`my_robot_perception/config/params.yaml`)

| Parameter | Default | Description |
| :--- | :---: | :--- |
| `kp` | `0.005` | Proportional gain for angular velocity control |
| `linear_speed` | `0.25` | Forward linear velocity (`m/s`) during target tracking |
| `search_angular_speed` | `0.45` | Rotational search speed (`rad/s`) when no target is detected |
| `stop_distance` | `0.45` | Minimum front LiDAR clearance (`m`) before triggering safety stop |
