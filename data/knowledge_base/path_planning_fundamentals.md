# Path Planning Fundamentals

## The Motion Planning Problem

Given:
- A robot with a known geometry and kinematics.
- An environment with known obstacles.
- A start configuration q_start and a goal configuration q_goal.

Find: A continuous path in configuration space from q_start to q_goal that does not collide with any obstacles.

This is the basic motion planning problem. In practice, additional requirements may include:
- Path optimality (shortest, smoothest, minimum energy).
- Kinodynamic constraints (velocity, acceleration, torque limits).
- Real-time performance.
- Dynamic obstacles.

## Completeness and Optimality

### Types of Completeness
- **Complete**: The algorithm is guaranteed to find a solution if one exists, and correctly report failure otherwise. Grid-based and combinatorial methods are complete.
- **Resolution complete**: Guaranteed to find a solution if one exists, given a sufficiently fine discretization. Fails if the resolution is too coarse.
- **Probabilistically complete**: The probability of finding a solution (if one exists) approaches 1 as the number of samples approaches infinity. RRT and PRM are probabilistically complete.

### Optimality
- **Optimal**: The algorithm finds the lowest-cost path. A* on a grid is optimal.
- **Asymptotically optimal**: The solution cost converges to the optimal cost as computation increases. RRT* and PRM* are asymptotically optimal.
- Most practical planners sacrifice optimality for speed and settle for feasible (collision-free) paths.

## Collision Detection

Collision detection is the computational bottleneck in sampling-based planning. Each candidate configuration or edge must be checked for collisions.

### Approaches
- **Mesh-mesh intersection**: Check if any triangles of the robot mesh intersect with obstacle meshes. Accurate but expensive.
- **Primitive-based**: Approximate the robot and obstacles with simple shapes (spheres, cylinders, boxes). Fast but less accurate.
- **Bounding Volume Hierarchies (BVH)**: Wrap meshes in nested bounding volumes (AABB, OBB, spheres). Quickly prune non-colliding pairs in broad-phase, then check detailed geometry in narrow-phase.
- **Signed Distance Fields (SDF)**: Precompute the distance to the nearest obstacle at every point in a 3D grid. Collision checking becomes a simple lookup. Used by CHOMP.

### Libraries
- **FCL (Flexible Collision Library)**: Used by MoveIt 2. Supports mesh-mesh, mesh-primitive, and continuous collision checking.
- **Bullet Physics**: Alternative collision checker in MoveIt 2. Good performance for complex scenes.
- **HPP-FCL**: A fork of FCL with additional features, used in Pinocchio.

## Configuration Space Representations

### Explicit Representation
Decompose the configuration space into free and obstacle regions. Only feasible for low-dimensional robots (2-3 DOF). Methods:
- Cell decomposition: Divide C-space into cells, mark each as free or obstacle.
- Visibility graphs: Connect vertices of C-space obstacles that can see each other.

### Implicit Representation
Do not explicitly construct C-space. Instead, use collision checking to test individual configurations. This is the approach used by sampling-based planners and is necessary for high-dimensional robots.

## Grid-Based Planning

### A* Algorithm
A* finds the shortest path on a graph (or grid) using a heuristic function. It maintains an open list of nodes to explore and a closed list of explored nodes.

f(n) = g(n) + h(n)

Where g(n) is the cost from start to n, and h(n) is the heuristic estimate from n to goal. With an admissible heuristic, A* is optimal.

### Dijkstra's Algorithm
A special case of A* with h(n) = 0. Optimal but explores more nodes than A*.

### Limitations of Grid-Based Methods
- Curse of dimensionality: the number of grid cells grows exponentially with DOF. A 7-DOF robot with 100 cells per joint would require 100^7 = 10^14 cells.
- Not practical for robots with more than 3-4 DOF.

## Potential Field Methods

### Artificial Potential Fields
The robot is modeled as a particle in a potential field:
- **Attractive potential**: Pulls the robot toward the goal. Typically quadratic: U_att = 0.5 * k_att * ||q - q_goal||^2.
- **Repulsive potential**: Pushes the robot away from obstacles. Typically: U_rep = 0.5 * k_rep * (1/d - 1/d_0)^2 when d < d_0, else 0, where d is distance to obstacle.

The robot follows the negative gradient of the total potential: F = -∇U_total.

### Local Minima Problem
The fundamental limitation of potential fields is local minima: the attractive and repulsive forces can cancel out at a point that is not the goal. The robot gets stuck.

Solutions:
- Random walks: add random perturbations to escape.
- Navigation functions: carefully designed potential fields guaranteed to have only one minimum (at the goal). Require full knowledge of the environment.
- Use potential fields only for local planning; combine with a global planner.

## Roadmap Methods

### Visibility Graphs
Connect all pairs of vertices (including start and goal) that can see each other (straight line does not intersect obstacles). Find the shortest path on this graph. Complete and optimal in 2D, but exponential in higher dimensions.

### Voronoi Diagrams
The Voronoi diagram of the obstacles is the set of points equidistant from two or more obstacles. Paths on the Voronoi diagram maximize clearance from obstacles. Useful for mobile robot navigation.

## Kinodynamic Planning

Standard motion planning finds geometric paths. Kinodynamic planning additionally considers:
- Velocity and acceleration constraints.
- Dynamic constraints (equations of motion).
- The output is a trajectory (path + timing), not just a path.

### Approaches
- **State-space RRT**: Extend RRT to plan in the state space (configuration + velocity). More complex because the tree must respect dynamics.
- **Trajectory optimization**: Start with a geometric path and optimize timing subject to dynamic constraints.
- **Time-optimal trajectory parameterization**: Given a geometric path, find the fastest way to traverse it while respecting velocity, acceleration, and torque limits. Used by MoveIt 2 (TOTP algorithm).

## Post-Processing

### Path Smoothing
Sampling-based planners produce jagged paths. Post-processing smooths them:
- **Shortcutting**: Randomly pick two points on the path, attempt to connect them with a straight line. If collision-free, replace the segment.
- **B-spline smoothing**: Fit a smooth B-spline curve to the waypoints.
- **Optimization-based smoothing**: Minimize a smoothness objective while staying collision-free.

### Time Parameterization
After obtaining a smooth geometric path, assign timestamps to each waypoint:
- Respect velocity and acceleration limits.
- Time-Optimal Trajectory Parameterization (TOTP) finds the fastest traversal.
- MoveIt 2 applies this automatically before sending trajectories to controllers.

## Multi-Robot Motion Planning

### Centralized Planning
Plan for all robots simultaneously in the combined configuration space. Guarantees optimality but the dimensionality grows linearly with the number of robots, making it intractable for many robots.

### Decoupled Planning
Plan for each robot independently, then resolve conflicts:
- **Prioritized planning**: Plan for robots one at a time in priority order, treating previously planned robots as moving obstacles.
- **Velocity tuning**: Plan paths independently, then adjust speeds to avoid collisions.

### Conflict-Based Search (CBS)
A two-level algorithm for multi-agent planning:
- Low level: Plan individually for each robot.
- High level: Detect conflicts between plans and resolve them by adding constraints.
- Optimal for multi-agent pathfinding on graphs.

## Real-Time Planning

For dynamic environments, the planner must run fast enough to react to changes:
- **Anytime planners**: Return a feasible solution quickly, then improve it if time permits. Examples: Anytime RRT*, ARA*.
- **Replanning**: Replan from the current state when the environment changes. D* Lite and similar algorithms efficiently update plans when the map changes.
- **MPC (Model Predictive Control)**: Plan short trajectories repeatedly at high frequency. Used for reactive manipulation and navigation.
