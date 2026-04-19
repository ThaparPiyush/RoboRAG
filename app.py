"""
RoboRAG — Streamlit web application.
A RAG-powered Q&A assistant for robotics and motion planning.
"""

import random
import time
import streamlit as st

st.set_page_config(
    page_title="RoboRAG — Robotics Q&A",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## RoboRAG")
    st.caption("Retrieval-Augmented Generation for Robotics & Motion Planning")
    st.divider()

    st.markdown("**Model:** OpenAI GPT-4o-mini")
    st.markdown("**Embeddings:** OpenAI text-embedding-3-small")
    st.markdown("**Vector DB:** ChromaDB")
    st.markdown("**Framework:** LangChain + Streamlit")
    st.divider()

    st.markdown("### Knowledge Base")
    st.markdown(
        """
        - Motion planning algorithms
        - MoveIt 2 framework
        - ROS 2 fundamentals
        - Robot manipulation & grasping
        - Kinematics & dynamics
        - Path planning fundamentals
        - SLAM & perception
        - Common robot platforms
        """
    )
    st.divider()
    st.markdown(
        "Built by **Piyush Thapar** for DS552 — Generative AI, WPI",
    )

# ── Lazy-load the RAG chain (cached across reruns) ──────────────────────────

@st.cache_resource(show_spinner="Loading RoboRAG pipeline …")
def load_pipeline():
    from rag_chain import build_rag_chain
    chain, retriever = build_rag_chain()
    return chain, retriever

chain, retriever = load_pipeline()

# ── Session state init ───────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "shown_examples" not in st.session_state:
    ALL_EXAMPLES = [
        "What motion planner should I use for a 7-DOF arm in a cluttered environment?",
        "How does RRT* differ from PRM for high-dimensional configuration spaces?",
        "What are the best practices for grasping transparent objects?",
        "Explain the MoveIt 2 planning pipeline and its components.",
        "What IK solvers are available in MoveIt 2 and how do they compare?",
        "How does Nav2 handle obstacle avoidance for mobile robots?",
        "What is the difference between STOMP and CHOMP?",
        "How does ROS 2 handle communication between nodes?",
        "What is the Jacobian matrix and how is it used in robotics?",
        "How does the pick-and-place pipeline work for a robot arm?",
        "What is tf2 in ROS 2 and why is it important?",
        "What are the advantages of a redundant robot arm?",
        "What collision checking libraries does MoveIt 2 support?",
        "Explain the difference between forward and inverse kinematics.",
        "What is SLAM and what are the main approaches?",
        "How does MoveIt Servo work for real-time robot control?",
        "What is the narrow passage problem in motion planning?",
        "What is ros2_control and how does it work?",
        "Compare the Franka Panda and UR5e robot arms.",
        "What is the configuration space in robotics?",
    ]
    st.session_state.shown_examples = random.sample(ALL_EXAMPLES, 6)

# ── Header ───────────────────────────────────────────────────────────────────

st.markdown(
    """
    <h1 style='text-align:center; margin-bottom:0;'>🤖 RoboRAG</h1>
    <p style='text-align:center; color:#94A3B8; margin-top:0;'>
        Ask me anything about motion planning, MoveIt 2, ROS 2, kinematics, grasping, and more.
    </p>
    """,
    unsafe_allow_html=True,
)

# ── Example question buttons (only before first interaction) ─────────────────

if not st.session_state.messages and st.session_state.pending_question is None:
    st.markdown("#### Try one of these questions:")
    cols = st.columns(2)
    for idx, ex in enumerate(st.session_state.shown_examples):
        col = cols[idx % 2]
        if col.button(ex, key=f"ex_{idx}", use_container_width=True):
            st.session_state.pending_question = ex
            st.rerun()

# ── Render chat history ─────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg:
            with st.expander("📄 View source documents"):
                for i, src in enumerate(msg["sources"], 1):
                    st.markdown(f"**Source {i} — {src['title']}**")
                    st.text(src["text"][:600])
                    st.divider()
            if "latency" in msg:
                st.caption(f"⏱ Response time: {msg['latency']:.1f}s")

# ── Determine the active question (pending button click OR chat input) ───────

active_question = None

if st.session_state.pending_question:
    active_question = st.session_state.pending_question
    st.session_state.pending_question = None

if user_input := st.chat_input("Ask a robotics question …"):
    active_question = user_input

# ── Process the question ─────────────────────────────────────────────────────

if active_question:
    st.session_state.messages.append({"role": "user", "content": active_question})
    with st.chat_message("user"):
        st.markdown(active_question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving context & generating answer …"):
            t0 = time.time()
            source_docs = retriever.invoke(active_question)
            answer = chain.invoke(active_question)
            latency = time.time() - t0

        st.markdown(answer)

        sources_data = [
            {"title": d.metadata.get("title", "Unknown"), "text": d.page_content}
            for d in source_docs
        ]
        with st.expander("📄 View source documents"):
            for i, src in enumerate(sources_data, 1):
                st.markdown(f"**Source {i} — {src['title']}**")
                st.text(src["text"][:600])
                st.divider()

        st.caption(f"⏱ Response time: {latency:.1f}s")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources_data,
            "latency": latency,
        }
    )
