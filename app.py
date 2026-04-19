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

    st.markdown("### Features")
    st.markdown(
        """
        - Multi-turn conversation memory
        - Retrieval confidence indicator
        - AI-generated follow-up questions
        - Answer feedback system
        - Source document citations
        """
    )
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

# ── Lazy-load RAG components (cached across reruns) ──────────────────────────

@st.cache_resource(show_spinner="Loading RoboRAG pipeline …")
def load_components():
    from rag_chain import get_vectorstore, get_llm
    return get_llm(), get_vectorstore()

llm, vs = load_components()

# ── Session state init ───────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = {}
if "shown_examples" not in st.session_state:
    ALL_EXAMPLES = [
        "What motion planner should I use for a 7-DOF arm in a cluttered environment?",
        "How does RRT* differ from PRM for high-dimensional spaces?",
        "What are the best practices for grasping transparent objects?",
        "Explain the MoveIt 2 planning pipeline and its components.",
        "What IK solvers are available in MoveIt 2?",
        "What is the difference between STOMP and CHOMP?",
        "How does ROS 2 handle communication between nodes?",
        "What is the Jacobian matrix and how is it used in robotics?",
        "How does the pick-and-place pipeline work for a robot arm?",
        "What collision checking libraries does MoveIt 2 support?",
        "Explain the difference between forward and inverse kinematics.",
        "What is SLAM and what are the main approaches?",
        "How does MoveIt Servo work for real-time robot control?",
        "What is the narrow passage problem in motion planning?",
        "Compare the Franka Panda and UR5e robot arms.",
        "What types of grippers are used in robot manipulation?",
        "How does the Denavit-Hartenberg convention work?",
        "What is impedance control in robot manipulation?",
    ]
    st.session_state.shown_examples = random.sample(ALL_EXAMPLES, 6)

# ── Helpers ──────────────────────────────────────────────────────────────────

def format_chat_history(messages, max_exchanges=3):
    """Format recent conversation as context for multi-turn memory."""
    if not messages:
        return ""
    recent = messages[-(max_exchanges * 2):]
    lines = []
    for msg in recent:
        role = "User" if msg["role"] == "user" else "Assistant"
        content = msg["content"]
        if role == "Assistant" and len(content) > 500:
            content = content[:500] + "…"
        lines.append(f"{role}: {content}")
    return "\n\n".join(lines)


def compute_confidence(scores):
    """Normalize ChromaDB relevance scores to an intuitive 0-100% range.
    Uses the best match score with scaling for OpenAI embeddings + L2 distance."""
    if not scores:
        return 0.0
    top_score = max(scores)
    normalized = min(1.0, top_score * 1.5)
    return max(0, normalized * 100)


def render_confidence(confidence_pct):
    """Display a colored confidence indicator."""
    if confidence_pct >= 70:
        color, level = "green", "High"
    elif confidence_pct >= 45:
        color, level = "orange", "Medium"
    else:
        color, level = "red", "Low"
    st.markdown(f"**Retrieval Confidence:** :{color}[{level} ({confidence_pct:.0f}%)]")
    if confidence_pct < 45:
        st.warning("This topic may not be well covered in the knowledge base.")


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

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            # Confidence indicator
            if "confidence" in msg:
                render_confidence(msg["confidence"])

            # Source documents
            if "sources" in msg:
                with st.expander("📄 View source documents"):
                    for j, src in enumerate(msg["sources"], 1):
                        st.markdown(f"**Source {j} — {src['title']}**")
                        st.text(src["text"][:600])
                        st.divider()

            # Latency
            if "latency" in msg:
                st.caption(f"⏱ Response time: {msg['latency']:.1f}s")

            # Feedback buttons
            fb_key = f"fb_{i}"
            if fb_key in st.session_state.feedback_given:
                fb = st.session_state.feedback_given[fb_key]
                st.caption(f"{'👍' if fb == 'up' else '👎'} Feedback recorded — thank you!")
            else:
                fc1, fc2, _ = st.columns([1, 1, 10])
                if fc1.button("👍", key=f"up_{i}"):
                    st.session_state.feedback_given[fb_key] = "up"
                    st.rerun()
                if fc2.button("👎", key=f"down_{i}"):
                    st.session_state.feedback_given[fb_key] = "down"
                    st.rerun()

            # Follow-up question buttons (only for the last assistant message)
            if i == len(st.session_state.messages) - 1 and "followups" in msg and msg["followups"]:
                st.markdown("**Suggested follow-ups:**")
                for fi, fq in enumerate(msg["followups"]):
                    if st.button(f"➡️ {fq}", key=f"followup_{i}_{fi}", use_container_width=True):
                        st.session_state.pending_question = fq
                        st.rerun()

# ── Determine the active question ────────────────────────────────────────────

active_question = None

if st.session_state.pending_question:
    active_question = st.session_state.pending_question
    st.session_state.pending_question = None

if user_input := st.chat_input("Ask a robotics question …"):
    active_question = user_input

# ── Process the question ─────────────────────────────────────────────────────

if active_question:
    from rag_chain import answer_question, generate_followups

    st.session_state.messages.append({"role": "user", "content": active_question})
    with st.chat_message("user"):
        st.markdown(active_question)

    with st.chat_message("assistant"):
        # Build chat history for multi-turn memory
        chat_history = format_chat_history(st.session_state.messages[:-1])

        with st.spinner("Retrieving context & generating answer …"):
            t0 = time.time()
            answer, source_docs, scores = answer_question(
                llm, vs, active_question, chat_history
            )
            latency = time.time() - t0

        st.markdown(answer)

        # Confidence indicator
        confidence_pct = compute_confidence(scores)
        render_confidence(confidence_pct)

        # Source documents
        sources_data = [
            {"title": d.metadata.get("title", "Unknown"), "text": d.page_content}
            for d in source_docs
        ]
        with st.expander("📄 View source documents"):
            for j, src in enumerate(sources_data, 1):
                st.markdown(f"**Source {j} — {src['title']}**")
                st.text(src["text"][:600])
                st.divider()

        st.caption(f"⏱ Response time: {latency:.1f}s")

        # Generate follow-up suggestions (validated against KB)
        with st.spinner("Generating follow-up suggestions …"):
            try:
                followups = generate_followups(llm, vs, active_question, answer)
            except Exception:
                followups = []

    msg_idx = len(st.session_state.messages)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources_data,
            "latency": latency,
            "confidence": confidence_pct,
            "followups": followups,
        }
    )
    st.rerun()
