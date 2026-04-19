# Motion Planning Algorithms

## Rapidly-Exploring Random Trees (RRT)

RRT is a sampling-based motion planning algorithm introduced by Steven LaValle in 1998. It works by incrementally building a tree rooted at the start configuration and growing it toward unexplored regions of the configuration space.

### How RRT Works
1. Sample a random point in configuration space.
2. Find the nearest node in the existing tree to that sample.
3. Extend from the nearest node toward the sample by a fixed step size.
4. If the extension is collision-free, add the new node to the tree.
5. Repeat until the tree reaches the goal region.

### Properties of RRT
- Probabilistically complete: given enough time, it will find a path if one exists.
- Not optimal: the paths found are typically jagged and suboptimal.
- Works well in high-dimensional spaces (6-DOF, 7-DOF robot arms).
- Does not require explicit construction of the configuration space.
- Biased toward exploring unexplored regions due to the Voronoi bias of random sampling.
- Time complexity grows with the dimensionality of the configuration space.

### When to Use RRT
- Quick feasibility checks in complex environments.
- High-dimensional planning problems where grid-based methods are infeasible.
- Single-query planning scenarios (one start, one goal).

---

## RRT* (RRT-Star)

RRT* was introduced by Karaman and Frazzoli in 2011 as an asymptotically optimal extension of RRT. It produces paths that converge to the optimal solution as the number of samples increases.

### Key Differences from RRT
- **Rewiring step**: After adding a new node, RRT* checks whether nearby nodes can be reached more cheaply through the new node. If so, it rewires the tree.
- **Near-neighbor search**: Uses a radius that shrinks as the tree grows, balancing exploration and optimization.
- **Cost tracking**: Each node stores its cost-to-come from the start.

### Properties of RRT*
- Asymptotically optimal: the solution cost converges to the true optimum.
- More computationally expensive than RRT due to the rewiring step.
- Produces smoother, shorter paths than RRT given sufficient samples.
- Still probabilistically complete.

### When to Use RRT*
- When path quality matters (e.g., minimizing joint travel, energy, or time).
- When you can afford more computation time for better solutions.
- Manipulation tasks where smooth paths reduce wear on actuators.

---

## Probabilistic Roadmap (PRM)

PRM was introduced by Kavraki, Svestka, Latombe, and Overmars in 1996. Unlike RRT, PRM is a multi-query planner that builds a roadmap of the free configuration space in a preprocessing phase.

### Two Phases of PRM
1. **Construction phase**: Sample N random configurations in free space. For each sample, attempt to connect it to its k nearest neighbors with straight-line paths. Store the resulting graph (roadmap).
2. **Query phase**: Given start and goal configurations, connect them to the nearest nodes in the roadmap and search the graph (e.g., A* or Dijkstra) for a path.

### Properties of PRM
- Multi-query: build the roadmap once, answer many queries quickly.
- Probabilistically complete in the limit.
- Not asymptotically optimal in its basic form (PRM* is the optimal variant).
- Works best in static environments where the roadmap can be reused.
- Struggles with narrow passages — random sampling may fail to find configurations in tight spaces.

### When to Use PRM
- Multiple planning queries in the same environment (e.g., a robot repeatedly picking from different bins).
- Environments that do not change frequently.
- When amortized query time matters more than preprocessing time.

### Narrow Passage Problem
PRM struggles when the free space contains narrow passages (e.g., a robot arm reaching through a gap between obstacles). Solutions include:
- Gaussian sampling: sample pairs of points and keep those near obstacle boundaries.
- Bridge test sampling: keep samples that are near two obstacles simultaneously.
- Adaptive sampling strategies that increase density in difficult regions.

---

## STOMP (Stochastic Trajectory Optimization for Motion Planning)

STOMP is an optimization-based motion planning algorithm that generates smooth, collision-free trajectories by iteratively improving a noisy initial trajectory.

### How STOMP Works
1. Start with an initial trajectory (e.g., straight line in joint space from start to goal).
2. Generate K noisy variations of the trajectory by adding correlated Gaussian noise.
3. Evaluate the cost of each noisy trajectory (collision cost + smoothness cost).
4. Combine the noisy trajectories using a weighted average, where lower-cost trajectories get higher weights.
5. Update the trajectory and repeat.

### Properties of STOMP
- Gradient-free: does not require gradient computation, making it suitable for non-differentiable cost functions.
- Produces smooth trajectories naturally due to the smoothness cost term.
- Can handle complex cost functions (e.g., visibility constraints, torque limits).
- May get stuck in local minima.
- Typically faster than sampling-based methods for smooth trajectory generation.

### When to Use STOMP
- When you need smooth trajectories (e.g., for real robot execution).
- When the cost function is not differentiable.
- Manipulation tasks where smoothness and naturalness matter.

---

## CHOMP (Covariant Hamiltonian Optimization for Motion Planning)

CHOMP is a gradient-based trajectory optimization method that minimizes a functional combining obstacle avoidance and trajectory smoothness.

### How CHOMP Works
1. Start with an initial trajectory (typically a straight line in joint space).
2. Compute the gradient of the objective function, which includes:
   - Obstacle cost: penalizes proximity to obstacles using a signed distance field.
   - Smoothness cost: penalizes high velocities and accelerations (measured by a covariant norm).
3. Update the trajectory using gradient descent (with a covariant update rule for better convergence).
4. Repeat until convergence.

### Properties of CHOMP
- Gradient-based: requires a differentiable cost function and precomputed distance fields.
- Produces very smooth trajectories.
- Fast convergence when the initial trajectory is reasonable.
- Requires a signed distance field of the environment, which must be precomputed.
- Can get stuck in local minima (e.g., the trajectory wraps around the wrong side of an obstacle).

### CHOMP vs. STOMP
- CHOMP uses gradients; STOMP is gradient-free.
- CHOMP is faster per iteration but requires differentiable costs.
- STOMP is more flexible with arbitrary cost functions.
- Both produce smooth trajectories and can get stuck in local minima.
- In practice, they are often comparable in performance for typical manipulation tasks.

---

## TrajOpt (Trajectory Optimization)

TrajOpt is a sequential convex optimization approach to motion planning developed by John Schulman et al.

### How TrajOpt Works
1. Formulate motion planning as a constrained optimization problem.
2. Use sequential quadratic programming (SQP) to solve it.
3. At each iteration, linearize the collision constraints and solve a convex subproblem.
4. Use a trust region to ensure the linearization is valid.

### Properties of TrajOpt
- Very fast convergence (often fewer than 10 iterations).
- Handles continuous collision checking via convex-convex swept-volume checks.
- Supports both joint-space and Cartesian-space constraints.
- Requires convex decomposition of obstacles.
- Can get stuck in local minima like other optimization methods.

---

## Comparison of Motion Planning Algorithms

| Algorithm | Type | Optimal | Smooth | Speed | Best For |
|-----------|------|---------|--------|-------|----------|
| RRT | Sampling | No | No | Fast | Quick feasibility, high-dim |
| RRT* | Sampling | Asymptotic | Better | Slower | Quality paths with time budget |
| PRM | Sampling | No | No | Fast queries | Multi-query, static environments |
| STOMP | Optimization | Local | Yes | Medium | Smooth paths, non-diff costs |
| CHOMP | Optimization | Local | Yes | Medium | Smooth paths, diff costs |
| TrajOpt | Optimization | Local | Yes | Fast | Fast smooth planning |

## Sampling-Based vs. Optimization-Based Planners

Sampling-based planners (RRT, PRM) explore the configuration space by random sampling. They are probabilistically complete and work well in high-dimensional spaces, but the paths they produce are often jagged and require post-processing (smoothing).

Optimization-based planners (STOMP, CHOMP, TrajOpt) start with an initial trajectory and iteratively improve it. They produce smooth paths but can get stuck in local minima and require a reasonable initial guess. They work best when combined with a sampling-based planner that provides the initial trajectory.

A common pipeline in practice: use RRT or PRM to find an initial feasible path, then refine it with STOMP or CHOMP for smoothness.
