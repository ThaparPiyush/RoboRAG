# Robot Manipulation and Grasping

## Overview

Robot manipulation is the field of robotics concerned with using robot arms and hands to interact with objects in the environment. It encompasses grasping, pick-and-place, assembly, tool use, and dexterous manipulation.

## Grasping Fundamentals

### Grasp Types
- **Power grasp**: The object is held firmly by wrapping the fingers and palm around it. Provides high force and stability. Used for heavy or large objects.
- **Precision grasp**: The object is held with the fingertips. Provides fine control and dexterity. Used for small or delicate objects.
- **Pinch grasp**: A type of precision grasp using two fingers (or finger and thumb). Common with parallel-jaw grippers.

### Grasp Quality Metrics
- **Force closure**: A grasp is force-closure if it can resist any external wrench (force and torque) applied to the object. This is the gold standard for grasp quality.
- **Form closure**: A grasp that constrains all degrees of freedom of the object through geometry alone (without friction). Stricter than force closure.
- **Grasp wrench space**: The set of all wrenches that the grasp can exert on the object. A larger grasp wrench space indicates a more robust grasp.
- **Ferrari-Canny metric**: Measures the radius of the largest ball inscribed in the grasp wrench space. Higher values indicate more robust grasps.
- **Grasp stability**: Resistance to disturbances. A stable grasp maintains contact under perturbations.

### Antipodal Grasps
Two contact points form an antipodal grasp if the line connecting them passes through the object's center of mass and the surface normals at the contact points are opposed. Antipodal grasps with sufficient friction are always force-closure.

## Grasp Planning

### Analytical Grasp Planning
- Compute grasps based on object geometry and physics.
- Requires accurate object models (mesh or primitive).
- Methods: form/force closure analysis, wrench space optimization.
- Advantage: provable grasp quality guarantees.
- Disadvantage: requires accurate models, computationally expensive for complex objects.

### Data-Driven Grasp Planning
- Learn grasp configurations from data (simulation or real-world).
- Methods: GraspNet, GPD (Grasp Pose Detection), Contact-GraspNet, AnyGrasp.
- Input: point clouds, depth images, or RGB-D data.
- Output: 6-DOF grasp poses with quality scores.
- Advantage: generalizes to novel objects without explicit models.
- Disadvantage: requires training data, may not provide quality guarantees.

### Grasp Planning Pipeline (Typical)
1. Perceive the scene (RGB-D camera → point cloud).
2. Segment objects of interest.
3. Generate candidate grasps (analytical or data-driven).
4. Rank grasps by quality and reachability.
5. Plan a collision-free approach motion to the grasp pose.
6. Execute: approach → grasp → lift → transport → place.

## Gripper Types

### Parallel-Jaw Gripper
- Two flat fingers that move linearly toward each other.
- Simple, robust, widely used in industry.
- Limited to objects that fit between the jaws.
- Examples: Robotiq 2F-85, Franka Hand.

### Multi-Finger Hands
- Three or more fingers with multiple joints each.
- Can perform a wider range of grasps and in-hand manipulation.
- More complex control.
- Examples: Allegro Hand, Shadow Hand, LEAP Hand.

### Suction/Vacuum Grippers
- Use negative pressure to grip flat or smooth surfaces.
- Very common in warehouse and logistics applications.
- Cannot grip porous, rough, or very small objects.
- Often combined with parallel-jaw grippers in multi-modal end effectors.

### Soft Grippers
- Made of compliant materials that conform to object shapes.
- Gentle on objects — suitable for food, produce, delicate items.
- Less precise than rigid grippers.
- Examples: Soft Robotics mGrip, FinRay-based grippers.

## Pick and Place

### Standard Pick-and-Place Pipeline
1. **Perception**: Detect and localize target object.
2. **Grasp selection**: Choose a grasp pose.
3. **Pre-grasp approach**: Move to a pose offset from the grasp (typically 5-10 cm above/behind).
4. **Approach**: Linear motion to the grasp pose.
5. **Grasp**: Close the gripper.
6. **Lift**: Move straight up to clear the surface.
7. **Transport**: Move to the place location (free-space motion planning).
8. **Place approach**: Move to a pose above the place location.
9. **Place**: Lower and open the gripper.
10. **Retreat**: Move away from the placed object.

### Challenges in Pick and Place
- **Clutter**: Objects packed tightly together. The robot may need to push objects aside or pick in a specific order.
- **Occlusion**: Objects hidden behind other objects. May require active perception (moving the camera) or reasoning about occluded regions.
- **Unknown objects**: Objects not in the training set. Requires generalization in grasp planning and perception.
- **Transparent and reflective objects**: Depth sensors fail on these surfaces. Solutions: polarization cameras, multi-view stereo, learned depth completion.

## Compliant and Force-Controlled Manipulation

### Impedance Control
The robot behaves as a virtual spring-damper system. The controller computes torques based on the deviation from a desired position/orientation:

τ = K(x_desired - x_current) + D(ẋ_desired - ẋ_current)

Where K is the stiffness matrix and D is the damping matrix.

- Allows the robot to comply with external forces.
- Essential for tasks like insertion, polishing, and assembly.
- Supported by most modern robot arms (e.g., Franka Emika Panda, KUKA iiwa).

### Force/Torque Sensing
Many manipulation tasks require force feedback:
- Peg-in-hole insertion: feel when the peg contacts the hole edge.
- Surface following: maintain constant contact force.
- Tightening: apply a specific torque to a fastener.

Force/torque sensors are typically mounted at the wrist (between the last joint and the end effector).

## Dual-Arm Manipulation

### Challenges
- Coordinating two arms to manipulate a single object requires careful planning of both arm motions simultaneously.
- The combined configuration space is high-dimensional (e.g., 14-DOF for two 7-DOF arms).
- Must avoid collisions between the two arms, between arms and the object, and between arms and the environment.
- Closed-chain kinematics: when both arms hold the same object, they form a closed kinematic chain.

### Planning Approaches
- Plan in the combined configuration space (14-DOF) using RRT or PRM.
- Decompose into leader-follower: one arm leads, the other follows to maintain the grasp.
- Task-space coordination: specify the relative pose between the two end effectors.

## Grasping Transparent Objects

Transparent objects pose a significant challenge for standard depth sensors (structured light, ToF) because the infrared light passes through or reflects off the surface unpredictably.

### Solutions
- **Polarization cameras**: Detect surface normals from polarization patterns of reflected light.
- **Multi-view stereo**: Use multiple RGB cameras to triangulate depth.
- **Learned depth completion**: Train a neural network to predict depth of transparent objects from RGB + noisy depth input. Examples: ClearGrasp, TranspareNet.
- **Tactile sensing**: Use touch sensors to feel the object after contact.
- **Edge-based methods**: Detect object contours in RGB images and reason about geometry from silhouettes.
