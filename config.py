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
