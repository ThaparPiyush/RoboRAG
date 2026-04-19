# SLAM and Perception for Robotics

## SLAM (Simultaneous Localization and Mapping)

SLAM is the problem of building a map of an unknown environment while simultaneously tracking the robot's pose within it. It is a fundamental capability for autonomous mobile robots.

### Visual SLAM
Uses cameras as the primary sensor:
- **ORB-SLAM3**: State-of-the-art visual SLAM supporting monocular, stereo, and RGB-D cameras. Uses ORB features for tracking and loop closure.
- **LSD-SLAM**: Direct (featureless) monocular SLAM that operates on image intensities.
- **RTAB-Map**: Real-time appearance-based mapping. Supports RGB-D, stereo, and lidar. Well integrated with ROS 2. Good for large-scale environments.

### Lidar SLAM
Uses lidar scanners:
- **Cartographer**: Google's real-time SLAM for 2D and 3D lidar. Available in ROS 2.
- **LOAM (Lidar Odometry and Mapping)**: Separates odometry (high frequency) and mapping (low frequency) for real-time performance.
- **KISS-ICP**: Simple, robust lidar odometry using point-to-point ICP.

### Graph-Based SLAM
Modern SLAM systems formulate the problem as a factor graph:
- **Nodes**: Robot poses and landmark positions.
- **Edges (factors)**: Constraints from odometry, sensor observations, loop closures.
- **Optimization**: Minimize the total error across all constraints using nonlinear least squares (e.g., Gauss-Newton, Levenberg-Marquardt).
- Libraries: GTSAM, g2o, Ceres Solver.

## 3D Perception for Manipulation

### Point Clouds
A point cloud is a set of 3D points, typically captured by depth cameras or lidar. Each point has (x, y, z) coordinates and optionally color (RGB) and normal information.

#### Point Cloud Processing Pipeline
1. **Acquisition**: Capture from depth camera (Intel RealSense, Azure Kinect) or lidar.
2. **Filtering**: Remove noise, statistical outliers, and points outside the region of interest.
3. **Downsampling**: Reduce the number of points using voxel grid filtering.
4. **Segmentation**: Separate the scene into individual objects. Methods:
   - Plane segmentation (RANSAC): Remove the table/floor plane.
   - Euclidean clustering: Group nearby points into clusters.
   - Region growing: Grow segments from seed points based on normal similarity.
5. **Registration**: Align multiple point clouds using ICP (Iterative Closest Point) or feature matching.

### Depth Cameras
- **Structured light** (Intel RealSense D435): Projects an infrared pattern and triangulates depth from the deformation. Good indoors, struggles in sunlight.
- **Time-of-Flight (ToF)** (Azure Kinect, PMD): Measures the time for light to travel to the scene and back. Works at longer range but lower resolution.
- **Stereo** (ZED camera): Uses two cameras to triangulate depth. Works outdoors but requires texture in the scene.

### Object Detection and Pose Estimation
For manipulation, the robot needs to know what objects are in the scene and where they are (6-DOF pose).

#### Methods
- **Template matching**: Match a known 3D model to the observed point cloud using ICP or feature-based registration.
- **Deep learning**: Networks like PoseCNN, DenseFusion, and FoundationPose predict object poses from RGB-D images.
- **Category-level pose estimation**: Predict poses for novel objects in known categories (e.g., any mug, any bottle). Methods: NOCS (Normalized Object Coordinate Space).

### Octomap
Octomap is a probabilistic 3D mapping framework based on octrees. It represents the environment as a 3D occupancy grid where each voxel stores a probability of being occupied.
- Memory-efficient due to octree structure (empty space is not stored).
- Supports multi-resolution queries.
- Integrated with MoveIt 2 for collision avoidance.
- Updated incrementally from depth sensor data.

## Sensor Fusion

Combining data from multiple sensors improves robustness and accuracy:
- **Camera + lidar**: Lidar provides accurate depth; cameras provide color and texture. Fuse by projecting lidar points onto camera images.
- **Camera + IMU**: IMU provides high-frequency orientation updates; camera provides absolute position. Fused in visual-inertial odometry (VIO) systems like VINS-Mono, MSCKF.
- **Multiple cameras**: Stereo or multi-view setups for wider field of view and better depth estimation.

### Extended Kalman Filter (EKF)
A common fusion algorithm:
- Prediction step: Use the motion model (odometry, IMU) to predict the state.
- Update step: Use sensor observations to correct the prediction.
- Assumes Gaussian noise and linearizes nonlinear models.
- Used in `robot_localization` package in ROS 2.

## Semantic Perception

Beyond geometry, understanding what objects are and their properties:
- **Object recognition**: Classify objects in the scene (e.g., YOLO, Faster R-CNN, SAM).
- **Semantic segmentation**: Label every pixel/point with a class (e.g., table, cup, obstacle).
- **Instance segmentation**: Distinguish individual object instances.
- **Scene graphs**: Represent the scene as a graph of objects and their relationships.

## Calibration

### Camera Intrinsic Calibration
Determine the camera's internal parameters (focal length, principal point, distortion coefficients) using a calibration target (e.g., checkerboard, ChArUco board).

### Hand-Eye Calibration
Determine the transform between the camera and the robot end effector (eye-in-hand) or between the camera and the robot base (eye-to-hand). Methods:
- Tsai-Lenz algorithm
- Park-Martin dual quaternion method
- Collect multiple poses of a calibration target and solve AX=XB.

### Camera-to-Robot Calibration
Essential for transforming perceived object poses from the camera frame to the robot frame for manipulation.
