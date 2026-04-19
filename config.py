"""RoboRAG configuration — central place for all tunable parameters."""

import os

# --- LLM ---
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.2
LLM_MAX_OUTPUT_TOKENS = 1024

# --- Embeddings ---
EMBEDDING_MODEL = "text-embedding-3-small"

# --- ChromaDB ---
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "roborag"

# --- Chunking ---
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# --- Retrieval ---
TOP_K = 5

# --- Data ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "knowledge_base")

# --- Prompt ---
SYSTEM_PROMPT = """\
You are **RoboRAG**, an expert assistant for robotics, motion planning, and \
the ROS 2 / MoveIt 2 ecosystem.

Rules you MUST follow:
1. Answer the user's question using ONLY the retrieved context below.
2. If the context does not contain enough information, say: \
"I don't have enough information in my knowledge base to answer this."
3. Cite the source document for every major claim using [Source: <title>].
4. Be concise but thorough. Use bullet points or numbered lists when helpful.
5. Never invent function names, API calls, or paper results that are not in the context.
"""

RAG_PROMPT_TEMPLATE = """\
{system_prompt}

--- Retrieved Context ---
{context}
--- End Context ---

User question: {question}

Answer:"""

# V2 prompt with multi-turn conversation memory
RAG_PROMPT_TEMPLATE_V2 = """\
{system_prompt}

--- Conversation History ---
{chat_history}
--- End History ---

--- Retrieved Context ---
{context}
--- End Context ---

User question: {question}

Answer:"""

FOLLOWUP_PROMPT_TEMPLATE = """\
Based on this robotics Q&A exchange, suggest exactly 3 brief follow-up questions \
the user might ask next. Keep each question under 15 words.

STRICT RULES for generating follow-up questions:
1. Only ask about CONCEPTS, COMPARISONS, or HOW THINGS WORK — never about \
   implementation steps, installation, configuration, code, tutorials, or setup.
2. Stay strictly within these knowledge base topics:
   - Motion planning algorithms: RRT, RRT*, PRM, STOMP, CHOMP, TrajOpt, their properties and trade-offs
   - MoveIt 2: planning pipeline, collision checking (FCL, Bullet), MoveIt Servo, Task Constructor, OMPL integration
   - ROS 2: nodes, topics, services, actions, tf2, ros2_control, Nav2, URDF, Xacro, DDS
   - Robot manipulation: pick-and-place, grasp planning, gripper types, force/impedance control, dual-arm
   - Kinematics & dynamics: forward/inverse kinematics, Jacobian, DH convention, singularities, redundancy, workspace
   - Path planning: configuration space, A*, potential fields, collision detection, completeness, optimality
   - SLAM & perception: visual SLAM, lidar SLAM, point clouds, depth cameras, sensor fusion, calibration
   - Robot platforms: Franka Panda, UR5e, KUKA iiwa, Gazebo, Isaac Sim, MuJoCo
3. Each question should ask "What is...", "How does X compare to Y...", "What are the properties of...", \
   "Why is X important...", or "What are the trade-offs between...".
4. NEVER ask "How do I implement...", "How to configure...", "How to set up...", or "What tools/packages...".

Question: {question}
Answer: {answer}

Respond with exactly 3 questions, one per line, numbered 1-3. No other text."""
