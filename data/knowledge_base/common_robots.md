# Common Robot Platforms for Research and Industry

## Franka Emika Panda

The Franka Emika Panda is a 7-DOF collaborative robot arm widely used in research.

### Specifications
- Degrees of freedom: 7 (redundant for 6-DOF tasks)
- Payload: 3 kg
- Reach: 855 mm
- Repeatability: ±0.1 mm
- Weight: 18 kg (arm only)
- Integrated torque sensors in all 7 joints
- Integrated parallel-jaw gripper (Franka Hand) with force sensing

### Key Features
- Torque-controlled: enables compliant, force-sensitive manipulation.
- Built-in collision detection and reflex behaviors.
- Well-supported in ROS 2 and MoveIt 2 via the franka_ros2 package.
- Commonly used for research in grasping, contact-rich manipulation, and learning from demonstration.

### Software Integration
- franka_ros2: Official ROS 2 driver. Provides hardware interface for ros2_control.
- libfranka: C++ library for direct low-level control at 1 kHz.
- Supported in Gazebo and Isaac Sim for simulation.

---

## Universal Robots (UR5, UR5e, UR10, UR10e)

Universal Robots are the most widely deployed collaborative robots in industry.

### UR5e Specifications
- Degrees of freedom: 6
- Payload: 5 kg
- Reach: 850 mm
- Repeatability: ±0.03 mm
- Weight: 20.6 kg
- Built-in force/torque sensor at the tool flange

### Key Features
- Easy to program via the teach pendant (no coding required for simple tasks).
- UR+ ecosystem: certified accessories and software plugins.
- Excellent ROS 2 and MoveIt 2 support via Universal_Robots_ROS2_Driver.
- Widely used in industrial pick-and-place, machine tending, and assembly.

---

## KUKA iiwa (Intelligent Industrial Work Assistant)

### Specifications
- Degrees of freedom: 7
- Payload: 7 kg (iiwa 7) or 14 kg (iiwa 14)
- Reach: 800 mm (iiwa 7) or 820 mm (iiwa 14)
- Torque sensors in all joints
- Designed for human-robot collaboration

### Key Features
- High-precision torque control for force-sensitive tasks.
- Compliant behavior via impedance control.
- Used in automotive assembly, medical robotics, and research.
- ROS 2 support available through community drivers.

---

## ABB Robots (IRB series)

ABB is a major industrial robot manufacturer. Their robots are known for speed and precision.
- Primarily used in manufacturing: welding, painting, assembly, palletizing.
- 4-DOF to 6-DOF arms with payloads from 3 kg to 800 kg.
- ABB RobotStudio software for programming and simulation.
- ROS 2 support via abb_robot_driver.

---

## Mobile Manipulators

### TIAGo (PAL Robotics)
- Mobile base + 7-DOF arm + parallel gripper.
- Omnidirectional mobile base.
- Full ROS 2 and MoveIt 2 support.
- Used in service robotics research and competitions.

### Fetch Robotics
- Mobile base + 7-DOF arm.
- Designed for warehouse logistics and research.
- ROS 2 compatible.

### Hello Robot Stretch
- Compact mobile manipulator for home environments.
- Telescoping arm with 3-DOF + mobile base.
- Lightweight and affordable.
- Active open-source ROS 2 community.

---

## Simulation Environments

### Gazebo (Classic and Ignition/Garden)
- The most widely used robot simulator in the ROS ecosystem.
- Physics engines: ODE, Bullet, DART, Simbody.
- Sensor simulation: cameras, lidar, IMU, contact sensors.
- ROS 2 integration via gazebo_ros2_control and ros_gz.

### NVIDIA Isaac Sim
- GPU-accelerated robot simulation built on Omniverse.
- Photorealistic rendering for synthetic data generation.
- Physics via PhysX 5.
- Supports ROS 2, MoveIt 2, and Nav2.
- Domain randomization for sim-to-real transfer.

### PyBullet
- Python bindings for the Bullet physics engine.
- Lightweight and easy to use.
- Popular for reinforcement learning research.
- Supports URDF loading, joint control, and camera simulation.

### MuJoCo
- High-performance physics simulator developed by DeepMind.
- Accurate contact dynamics.
- Fast simulation (faster than real-time for most robots).
- Widely used in robot learning and control research.
- Free and open-source since 2022.
