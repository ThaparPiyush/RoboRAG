# ROS 2 Fundamentals

## What is ROS 2?

ROS 2 (Robot Operating System 2) is an open-source middleware framework for building robot applications. Despite its name, ROS 2 is not an operating system — it is a set of libraries, tools, and conventions that simplify the development of complex robot software.

ROS 2 is the successor to ROS 1 and addresses its limitations: real-time support, multi-robot systems, security, and production-readiness. ROS 2 is built on top of DDS (Data Distribution Service), an industry-standard communication middleware.

## Key Concepts

### Nodes
A node is a single-purpose process that performs computation. In ROS 2, a robot system is typically composed of many nodes, each responsible for a specific function:
- A camera node that publishes images
- A perception node that detects objects
- A planning node that computes trajectories
- A controller node that sends commands to motors

Nodes communicate with each other via topics, services, and actions.

### Topics
Topics are named buses for asynchronous, many-to-many communication. A node publishes messages to a topic; any number of nodes can subscribe to that topic.
- **Publisher**: Sends messages to a topic.
- **Subscriber**: Receives messages from a topic.
- Messages are typed (e.g., `sensor_msgs/msg/Image`, `geometry_msgs/msg/Twist`).
- Topics use a publish-subscribe pattern — publishers and subscribers are decoupled.

Common topics in robotics:
- `/joint_states`: Current joint positions, velocities, and efforts.
- `/cmd_vel`: Velocity commands for mobile robots.
- `/camera/image_raw`: Raw camera images.
- `/tf`: Coordinate frame transforms.

### Services
Services are synchronous, one-to-one request-response communication. A service server advertises a service; a client sends a request and waits for a response.
- Used for discrete operations: "compute IK for this pose", "enable motor", "set mode".
- Not suitable for streaming data (use topics instead).

### Actions
Actions are for long-running tasks with feedback. An action server accepts a goal, provides periodic feedback during execution, and returns a result when done.
- Used for tasks like "move to pose", "navigate to waypoint", "execute trajectory".
- Supports cancellation — the client can cancel an ongoing action.
- Built on top of topics and services internally.

Examples:
- `FollowJointTrajectory`: Execute a joint trajectory on the robot arm.
- `NavigateToPose`: Navigate a mobile robot to a target pose.

### Parameters
Parameters are configuration values that nodes can declare, get, and set at runtime. They are typed (bool, int, float, string, arrays) and can be loaded from YAML files.

### Launch Files
Launch files define how to start and configure a set of nodes. In ROS 2, launch files are written in Python, XML, or YAML. They specify:
- Which nodes to start
- Parameter files to load
- Topic remappings
- Namespace assignments
- Lifecycle transitions

## ROS 2 Communication: DDS

ROS 2 uses DDS (Data Distribution Service) as its underlying communication middleware. DDS provides:
- **Quality of Service (QoS)**: Fine-grained control over message delivery guarantees.
  - Reliability: best-effort vs. reliable delivery
  - Durability: transient-local (late subscribers get last message) vs. volatile
  - History: keep-all vs. keep-last-N
  - Deadline, liveliness, lifespan
- **Discovery**: Nodes automatically discover each other on the network without a central broker (unlike ROS 1's rosmaster).
- **Security**: Built-in encryption, authentication, and access control via SROS2.

Multiple DDS implementations are available: Fast DDS (default), Cyclone DDS, Connext DDS.

## tf2: Transform Library

tf2 manages coordinate frame transforms in ROS 2. It maintains a tree of transforms and allows querying the transform between any two frames at any point in time.

Key concepts:
- **Frames**: Named coordinate frames (e.g., `base_link`, `camera_link`, `world`).
- **Static transforms**: Fixed transforms that don't change (e.g., camera mounted on robot).
- **Dynamic transforms**: Transforms that change over time (e.g., joint-driven link transforms).
- The transform tree must be a tree (no loops) with a single root.

Common usage:
- "What is the pose of the end effector in the world frame?"
- "Transform this point cloud from the camera frame to the base frame."

## ros2_control

ros2_control is a framework for real-time robot control in ROS 2. It provides:

### Hardware Interface
An abstraction layer between controllers and hardware. Hardware interfaces define:
- **Command interfaces**: Values sent to hardware (e.g., position, velocity, effort commands).
- **State interfaces**: Values read from hardware (e.g., current positions, velocities).

### Controller Manager
Manages the lifecycle of controllers. Handles loading, configuring, activating, deactivating, and unloading controllers.

### Common Controllers
- **Joint Trajectory Controller**: Executes joint-space trajectories. This is what MoveIt 2 typically sends trajectories to.
- **Forward Command Controller**: Directly forwards commands to hardware.
- **Diff Drive Controller**: Controls differential-drive mobile robots.
- **Gripper Action Controller**: Controls parallel-jaw grippers.

## Navigation 2 (Nav2)

Nav2 is the ROS 2 navigation framework for mobile robots. It provides:
- **Costmaps**: 2D or 3D grid maps representing obstacle costs. Updated from sensor data (lidar, depth cameras).
- **Global Planner**: Plans a path from current position to goal on the costmap (e.g., NavFn, Smac).
- **Local Planner (Controller)**: Follows the global path while avoiding dynamic obstacles (e.g., DWB, MPPI, RPP).
- **Recovery Behaviors**: Actions to take when the robot is stuck (e.g., spin in place, clear costmap, back up).
- **Behavior Trees**: Nav2 uses behavior trees (via BehaviorTree.CPP) to orchestrate the navigation pipeline.

## URDF (Unified Robot Description Format)

URDF is an XML format that describes a robot's physical structure:
- **Links**: Rigid bodies with visual geometry, collision geometry, and inertial properties.
- **Joints**: Connections between links. Types: revolute, prismatic, fixed, continuous, floating, planar.
- **Transmissions**: Map joints to actuators (used by ros2_control).

Limitations of URDF:
- Cannot represent closed kinematic chains (only trees).
- Does not support parameterization — use Xacro macros for templating.

## Xacro

Xacro (XML Macros) is a macro language for URDF files. It allows:
- Parameterized macros (e.g., define a wheel once, instantiate it four times with different positions).
- Properties and math expressions.
- Conditional blocks.
- Including other Xacro files.

## ROS 2 Lifecycle Nodes

Lifecycle (managed) nodes have a state machine that controls their initialization and teardown:
1. **Unconfigured**: Node is loaded but not configured.
2. **Inactive**: Node is configured but not processing data.
3. **Active**: Node is fully operational.
4. **Finalized**: Node is shut down.

Transitions: configure, activate, deactivate, cleanup, shutdown.

Lifecycle nodes ensure deterministic startup and shutdown ordering in complex robot systems.

## Common ROS 2 Packages for Manipulation

- **moveit2**: Motion planning and manipulation.
- **ros2_control**: Hardware abstraction and controllers.
- **ros2_controllers**: Standard controllers (joint trajectory, gripper, etc.).
- **robot_state_publisher**: Publishes robot transforms from URDF and joint states.
- **joint_state_publisher**: Publishes fake joint states (for visualization/testing).
- **rviz2**: 3D visualization tool.
- **gazebo_ros2**: Simulation integration with Gazebo.
