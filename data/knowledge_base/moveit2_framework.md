# MoveIt 2 Framework

## Overview

MoveIt 2 is the most widely used open-source software framework for robotic manipulation. It provides functionality for motion planning, manipulation, 3D perception, kinematics, control, and navigation. MoveIt 2 is built on top of ROS 2 (Robot Operating System 2) and is designed for real-time robot control.

MoveIt 2 is the ROS 2 port of the original MoveIt framework (which was built on ROS 1). It was re-architected to leverage ROS 2 features such as real-time support, improved security, and multi-robot capabilities.

## MoveIt 2 Architecture

### Core Components

1. **Move Group**: The central node that integrates all MoveIt components. It provides actions and services for motion planning, pick-and-place, and kinematics queries.

2. **Planning Scene**: Maintains the world representation, including:
   - Robot state (joint positions, link transforms)
   - Collision objects in the environment
   - Attached objects (objects the robot is holding)
   - Allowed collision matrix (which pairs of links/objects can be in collision)

3. **Planning Pipeline**: Takes a motion plan request and returns a trajectory. Consists of:
   - A planner (e.g., OMPL, Pilz, STOMP)
   - Optional plan request adapters (pre-processing)
   - Optional plan response adapters (post-processing, such as trajectory smoothing)

4. **Kinematics Solvers**: Compute forward and inverse kinematics.
   - Default: KDL (Kinematics and Dynamics Library)
   - Alternatives: IKFast (analytical, faster), TRAC-IK (more robust than KDL), BioIK

5. **Controller Manager**: Interfaces with the robot's hardware controllers to execute trajectories.

### Planning Scene Monitor
The Planning Scene Monitor keeps the planning scene up to date by subscribing to:
- Joint state messages from the robot
- Collision object updates from perception pipelines
- Attached object notifications from the manipulation pipeline

## Motion Planners in MoveIt 2

### OMPL (Open Motion Planning Library)
OMPL is the default planning library in MoveIt 2. It provides implementations of many sampling-based planners:
- RRT, RRT*, RRT-Connect
- PRM, PRM*
- EST (Expansive Space Trees)
- KPIECE (Kinematic Planning by Interior-Exterior Cell Exploration)
- BiEST, SBL, and many more

OMPL does not perform collision checking itself — it uses MoveIt's collision checking (via FCL or Bullet) as a validity checker.

**RRT-Connect** is the default planner in MoveIt 2's OMPL configuration. It grows two trees simultaneously (one from start, one from goal) and attempts to connect them. It is very fast for finding feasible paths but does not optimize path quality.

### Pilz Industrial Motion Planner
Designed for industrial applications where deterministic, predictable motion is required:
- **PTP (Point-to-Point)**: Joint-space interpolation with trapezoidal velocity profiles.
- **LIN (Linear)**: Cartesian linear motion with constant orientation.
- **CIRC (Circular)**: Circular arc motion in Cartesian space.

Use Pilz when you need precise, repeatable Cartesian motions (e.g., welding, painting, assembly).

### STOMP in MoveIt 2
MoveIt 2 includes a STOMP planner plugin. It is particularly useful when:
- You need smooth trajectories without post-processing.
- The task involves navigating around obstacles where optimization helps.
- You want to incorporate custom cost functions.

### CHOMP in MoveIt 2
MoveIt 2 also provides a CHOMP planner plugin. It requires a precomputed distance field of the environment. Best for scenarios where a signed distance field is available and the environment is relatively static.

## MoveIt 2 Configuration

### SRDF (Semantic Robot Description Format)
The SRDF file complements the URDF by defining:
- Planning groups (e.g., "arm", "gripper") — which joints belong to which group.
- Default poses (e.g., "home", "ready", "extended").
- End effectors (which link is the end effector, which group controls it).
- Disabled collision pairs (pairs of links that can never collide, to speed up collision checking).
- Virtual joints (e.g., connecting the robot base to the world frame).

### MoveIt Setup Assistant
The MoveIt Setup Assistant is a GUI tool that generates the configuration files needed for MoveIt 2:
- SRDF
- Joint limits YAML
- Kinematics YAML (solver selection and parameters)
- OMPL planning YAML (planner selection and parameters)
- Controllers YAML
- Launch files

### Joint Limits
MoveIt 2 respects joint limits defined in the URDF and allows overriding them in a YAML file:
- Position limits
- Velocity limits
- Acceleration limits (used for time parameterization)

## Collision Checking in MoveIt 2

MoveIt 2 uses the **FCL (Flexible Collision Library)** or **Bullet Physics** for collision checking.

### FCL
- Default collision checker in MoveIt 2.
- Supports mesh-mesh, mesh-primitive, and primitive-primitive collision checks.
- Uses BVH (Bounding Volume Hierarchy) for efficient broad-phase collision detection.

### Bullet
- Alternative collision checker, often faster for complex scenes.
- Supports continuous collision checking (detecting collisions along a trajectory, not just at discrete waypoints).

### Allowed Collision Matrix (ACM)
The ACM is a matrix that specifies which pairs of links/objects should be checked for collision. Disabling unnecessary collision pairs (e.g., adjacent links that can never collide) significantly speeds up planning.

## Trajectory Execution

After planning, MoveIt 2 sends the trajectory to the robot's controllers. The pipeline is:
1. **Time parameterization**: Add timestamps and velocity/acceleration profiles to the trajectory. MoveIt 2 uses the Time-Optimal Trajectory Parameterization (TOTP) algorithm by default.
2. **Controller interface**: MoveIt 2 communicates with ros2_control controllers via the FollowJointTrajectory action.
3. **Execution monitoring**: MoveIt 2 monitors execution and can replan if the robot deviates from the trajectory.

## MoveIt Task Constructor (MTC)

MTC is a framework for defining complex manipulation tasks as a sequence of stages:
- **Generator stages**: Generate possible states (e.g., grasp poses, place poses).
- **Propagator stages**: Propagate solutions forward or backward (e.g., approach, retreat).
- **Connector stages**: Connect two states (e.g., plan a free-space motion between approach and retreat).

Example pick-and-place pipeline with MTC:
1. Open gripper
2. Move to pre-grasp pose
3. Approach object (linear motion)
4. Close gripper
5. Lift object
6. Move to place location
7. Lower object
8. Open gripper
9. Retreat

MTC allows defining these stages declaratively and automatically plans the complete sequence.

## MoveIt Servo

MoveIt Servo enables real-time, low-latency control of the robot arm. It accepts:
- Twist commands (Cartesian velocities)
- Joint velocity commands

Use cases:
- Teleoperation
- Visual servoing
- Force-guided motion
- Joystick control

MoveIt Servo runs at high frequency (typically 100-1000 Hz) and performs real-time collision checking to ensure safety.

## Common MoveIt 2 Usage Patterns

### Planning to a Joint Goal
Specify target joint values for all joints in the planning group. The planner finds a collision-free path from the current state to the target.

### Planning to a Pose Goal
Specify a target 6-DOF pose for the end effector. MoveIt 2 uses IK to find a target joint configuration, then plans to it. Multiple IK solutions may exist; the planner may try several.

### Cartesian Path Planning
Compute a path that follows a sequence of Cartesian waypoints. The `computeCartesianPath` function interpolates between waypoints and checks each interpolated point for IK feasibility and collisions. Returns the fraction of the path that was successfully computed.

### Planning with Constraints
MoveIt 2 supports path constraints:
- **Orientation constraints**: Keep the end effector at a fixed orientation (e.g., holding a cup upright).
- **Position constraints**: Keep the end effector within a region.
- **Joint constraints**: Keep specific joints within ranges.
- **Visibility constraints**: Keep a sensor pointed at a target.

Planning with constraints is significantly harder and slower than unconstrained planning. OMPL's constrained planning capabilities (e.g., AtlasStateSpace, ProjectedStateSpace) handle this.
