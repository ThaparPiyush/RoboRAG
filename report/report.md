# RoboRAG: A Retrieval-Augmented Generation Web Application for Robot Task Planning and Motion Planning Assistance

**Course:** DS552 — Generative AI  
**Instructor:** Dr. Narahara Chari Dingari  
**Student:** Piyush Thapar  
**Institution:** Worcester Polytechnic Institute  
**Date:** April 2026

---

## 1. Project Title

**RoboRAG: A Retrieval-Augmented Generation Web Application for Robot Task Planning and Motion Planning Assistance**

---

## 2. Introduction and Objective

### Introduction

Robotics researchers and engineers face a recurring challenge: the knowledge they need to make informed decisions about motion planners, manipulation strategies, sensor configurations, and software frameworks is scattered across academic papers, documentation pages, tutorials, and forum discussions. A graduate student trying to choose between RRT\* and STOMP for a 7-DOF arm might need to search through three arXiv papers, a half-finished ROS Answers thread, and a MoveIt GitHub issue before finding a useful answer.

Large Language Models (LLMs) have demonstrated impressive natural-language understanding and generation capabilities, but they frequently hallucinate facts in specialized technical domains. In robotics specifically, LLMs have been observed to confidently recommend API functions that do not exist or describe algorithm behaviors that are factually incorrect. This limits their usefulness as reliable technical assistants.

Retrieval-Augmented Generation (RAG) addresses this fundamental limitation by grounding the LLM's responses in actual retrieved documents. Rather than relying on the model's parametric memory, RAG retrieves the most relevant passages from a curated knowledge base at inference time and instructs the LLM to synthesize its answer based on that context. This significantly improves factual accuracy and provides verifiable source citations.

### Objective

The objective of this project is to develop **RoboRAG**, a web application that serves as an intelligent question-answering assistant for robot task planning and motion planning. Users can ask natural-language questions such as:

- "What motion planner should I use for a 7-DOF arm in a cluttered environment?"
- "How does RRT\* differ from PRM for high-dimensional configuration spaces?"
- "What are the best practices for grasping transparent objects?"

The application retrieves relevant passages from a curated knowledge base of robotics documentation, then uses OpenAI's GPT-4o-mini model to synthesize a grounded, coherent answer along with source citations.

### Why RAG with GPT-4o-mini Is Suitable for This Use Case

A RAG architecture is ideal for domain-specific technical Q&A because:

1. **Factual grounding**: The LLM reads relevant documentation at inference time rather than relying on potentially outdated or incorrect parametric memory.
2. **Source transparency**: Every answer comes with retrievable source passages that the user can verify, which is critical in engineering domains where incorrect information can lead to hardware damage or safety issues.
3. **Focused domain coverage**: By curating the knowledge base, we control exactly what the system knows and can ensure comprehensive coverage of the target domain without noise from unrelated topics.
4. **High-quality generation**: GPT-4o-mini provides excellent instruction-following, reading comprehension, and summarization capabilities at a very low cost (~$0.15 per 1M input tokens), making it ideal for synthesizing coherent answers from retrieved context.

---

## 3. Selection of Generative AI Model

### Model Choice: OpenAI GPT-4o-mini

The project uses **OpenAI GPT-4o-mini** as the generative model, accessed through the OpenAI API via the `langchain-openai` integration.

| Criterion | Justification |
|-----------|--------------|
| **Performance** | GPT-4o-mini excels at reading comprehension, summarization, and instruction-following — the core requirements of a RAG pipeline. It consistently produces well-structured, cited answers. |
| **Cost-effectiveness** | At $0.15 per 1M input tokens and $0.60 per 1M output tokens, the entire project (development, evaluation, and deployment) costs under $2. |
| **API reliability** | OpenAI's API is production-grade with high uptime, generous rate limits, and consistent response quality. No rate-limit issues during development or evaluation. |
| **LangChain integration** | First-class support through `langchain-openai` provides seamless integration with the RAG orchestration framework. |
| **Context window** | 128K token context window easily accommodates the retrieved document chunks alongside the user's question. |
| **Latency** | Average response times of 3–5 seconds make the application interactive and responsive. |

### Embedding Model: OpenAI text-embedding-3-small

For vector embeddings, the project uses **OpenAI's `text-embedding-3-small`** model. This model converts both document chunks and user queries into 1536-dimensional dense vector representations for semantic similarity search. Key advantages:

- High-quality embeddings optimized for retrieval tasks.
- Very low cost ($0.02 per 1M tokens — embedding the entire knowledge base costs less than $0.01).
- Consistent with the OpenAI ecosystem, simplifying API key management.
- No local ML model needed, reducing deployment memory requirements.

### Alternatives Considered

- **Google Gemini 2.5 Flash (free tier)**: Initially tested but the free tier had severe rate limits (20 requests/day for generation, 100/minute for embeddings) that made development, evaluation, and reliable deployment impractical.
- **Mistral 7B (local via Ollama)**: Strong open-source option but requires significant RAM (4.5 GB) and cannot run on free cloud hosting platforms like Streamlit Cloud.
- **Groq API (free Mistral)**: Free but has reliability issues under load and rate-limiting that impacts user experience.

GPT-4o-mini provides the best combination of quality, reliability, generous rate limits, and extremely low cost.

---

## 4. Project Definition and Use Case

### Application Concept

RoboRAG is a **domain-specific question-answering system** for robotics and motion planning, built as an interactive web application with a chat interface. It is not a general-purpose chatbot — it is specifically designed to answer technical questions about motion planning algorithms, the MoveIt 2 framework, ROS 2, robot manipulation, kinematics, and related topics.

### How the Generative AI Model Is Integrated

The application follows a Retrieval-Augmented Generation (RAG) architecture with two stages:

**Offline stage (one-time ingestion):**
1. Curated robotics documents (covering motion planning, MoveIt 2, ROS 2, manipulation, kinematics, SLAM, and common robot platforms) are loaded and parsed.
2. Documents are split into overlapping chunks of approximately 800 tokens with 100-token overlap using LangChain's `RecursiveCharacterTextSplitter`.
3. Each chunk is embedded into a dense vector using OpenAI's `text-embedding-3-small` model.
4. Vectors are stored in a ChromaDB vector database with metadata (source document title and file path).

**Online stage (per user query):**
1. The user types a question in the Streamlit chat interface.
2. The question is embedded using the same embedding model.
3. ChromaDB performs a similarity search to retrieve the top-5 most relevant document chunks.
4. The retrieved chunks, along with the user's question and a system prompt, are assembled into a prompt.
5. The prompt is sent to GPT-4o-mini, which generates a grounded answer with source citations.
6. The answer and the source passages are displayed in the chat interface.

### Use Case Scenario

A robotics graduate student is setting up a manipulation pipeline and needs to choose between motion planners. They open RoboRAG and ask: "What motion planner should I use for a 7-DOF arm in a cluttered environment?" Within seconds, they receive an answer that recommends RRT or RRT-Connect as fast feasible path finders, explains that STOMP is beneficial for smooth trajectories in cluttered spaces, and mentions Pilz for deterministic motion — all with citations to the specific knowledge base documents. The student can expand the "Source Documents" section to read the original passages and verify the claims.

---

## 5. Implementation Plan

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM** | OpenAI GPT-4o-mini | Answer generation |
| **Embeddings** | OpenAI text-embedding-3-small | Document and query embedding |
| **Vector Database** | ChromaDB (local, persisted) | Semantic similarity search |
| **RAG Orchestration** | LangChain | Chain construction, retrieval, prompting |
| **Web Framework** | Streamlit | Interactive chat UI |
| **Language** | Python 3.10+ | All components |
| **Document Processing** | LangChain text splitters | Chunking |
| **Evaluation** | rouge-score, scikit-learn, psutil | Performance metrics |
| **Configuration** | python-dotenv | API key management |

### Web Framework: Streamlit

Streamlit was chosen for the web framework because:
- Native Python — no frontend (HTML/CSS/JS) code required.
- Built-in `st.chat_input` and `st.chat_message` components provide a polished chat interface.
- `st.cache_resource` caches the RAG pipeline across reruns for fast response times.
- Streamlit Cloud offers free, persistent hosting with one-click deployment from GitHub.

### Development Steps

1. **Data curation**: Authored 8 comprehensive markdown documents covering motion planning algorithms, MoveIt 2 framework, ROS 2 fundamentals, robot manipulation and grasping, kinematics and dynamics, path planning fundamentals, SLAM and perception, and common robot platforms. Each document is factually accurate and comprehensive, totaling approximately 15,000 words.

2. **Ingestion pipeline** (`ingest.py`): Reads all knowledge base files, chunks them using `RecursiveCharacterTextSplitter` (800 tokens, 100 overlap), embeds with OpenAI's `text-embedding-3-small`, and stores in ChromaDB. The entire ingestion completes in under 15 seconds with no rate-limit issues.

3. **RAG chain** (`rag_chain.py`): Constructs a LangChain chain that retrieves top-5 chunks from ChromaDB, formats them with source labels, builds a prompt using a strict system instruction (answer only from context, cite sources, say "I don't know" when appropriate), and generates via GPT-4o-mini.

4. **Streamlit application** (`app.py`): Chat-style interface with example questions for new users, expandable source document panels, response time display, and a sidebar with system information.

5. **Evaluation** (`evaluate.py`): Automated evaluation against 20 benchmark Q&A pairs measuring ROUGE, F1, retrieval precision, latency, and memory usage. Includes a no-RAG baseline comparison (GPT-4o-mini without retrieval) to quantify the improvement RAG provides.

6. **Deployment**: Pre-built ChromaDB committed to the GitHub repository; Streamlit Cloud loads it at startup and serves the app at a persistent URL.

---

## 6. Model Evaluation and Performance Metrics

### Evaluation Methodology

The system was evaluated against a benchmark set of 20 hand-crafted Q&A pairs covering the full breadth of the knowledge base. Each pair includes a question, a reference answer, and a set of relevant keywords for retrieval precision assessment. The evaluation script computes metrics automatically and also runs a **no-RAG baseline** (GPT-4o-mini answering the same questions without any retrieved context) to quantify the improvement that retrieval provides.

### Results — RAG (RoboRAG) vs. Baseline (GPT-4o-mini without RAG)

#### Generation Quality Comparison

| Metric | RAG (RoboRAG) | Baseline (No RAG) | Improvement |
|--------|:-------------:|:-----------------:|:-----------:|
| **ROUGE-1** | 0.5013 | 0.1978 | **+0.3035 (+153%)** |
| **ROUGE-2** | 0.2575 | 0.0591 | **+0.1984 (+336%)** |
| **ROUGE-L** | 0.3753 | 0.1243 | **+0.2510 (+202%)** |
| **Token F1** | 0.2683 | 0.1053 | **+0.1631 (+155%)** |

RAG delivers a **153% improvement in ROUGE-1** and a **336% improvement in ROUGE-2** over the standalone LLM. This dramatic improvement confirms that retrieval grounding is essential for domain-specific Q&A — the LLM alone does not have sufficiently detailed knowledge of robotics-specific topics like MoveIt 2 planners, ROS 2 architecture, or specific grasp planning techniques.

#### Retrieval Quality

| Metric | Score | Interpretation |
|--------|-------|---------------|
| **Precision@5** | 0.7700 | 77.0% of retrieved chunks contain relevant keywords |

A Precision@5 of 0.77 means that on average, 3.85 out of 5 retrieved chunks are relevant to the question. This is solid retrieval quality and demonstrates that the OpenAI embedding model and chunking strategy effectively identify relevant passages from the knowledge base.

#### Efficiency

| Metric | RAG (RoboRAG) | Baseline (No RAG) |
|--------|:-------------:|:-----------------:|
| **Average latency** | 4.85s | 9.62s |
| **Peak memory** | 338.6 MB | — |

The RAG pipeline is actually **faster** than the baseline because GPT-4o-mini generates shorter, more focused answers when given relevant context, compared to the longer, more general answers it produces without context. Memory consumption of 339 MB is well within Streamlit Cloud's 1 GB limit.

#### Per-Question Breakdown

| # | Question (abbreviated) | ROUGE-1 | ROUGE-L | F1 | P@5 | Latency |
|---|----------------------|---------|---------|-----|------|---------|
| 1 | Motion planner for 7-DOF arm | 0.427 | 0.250 | 0.244 | 0.60 | 4.0s |
| 2 | RRT\* vs PRM | 0.393 | 0.224 | 0.163 | 1.00 | 8.1s |
| 3 | Grasping transparent objects | 0.482 | 0.362 | 0.240 | 0.60 | 4.2s |
| 4 | MoveIt 2 planning pipeline | 0.379 | 0.253 | 0.194 | 1.00 | 3.7s |
| 5 | IK solvers in MoveIt 2 | 0.562 | 0.486 | 0.360 | 1.00 | 4.3s |
| 6 | STOMP vs CHOMP | 0.441 | 0.228 | 0.251 | 1.00 | 5.4s |
| 7 | ROS 2 communication | 0.358 | 0.179 | 0.194 | 1.00 | 5.1s |
| 8 | Jacobian matrix in robotics | 0.409 | 0.351 | 0.174 | 1.00 | 7.3s |
| 9 | Pick-and-place pipeline | 0.551 | 0.483 | 0.192 | 1.00 | 4.9s |
| 10 | tf2 in ROS 2 | 0.495 | 0.394 | 0.286 | 0.80 | 4.1s |
| 11 | Advantages of redundant arms | 0.604 | 0.417 | 0.394 | 0.40 | 2.6s |
| 12 | Collision checking in MoveIt 2 | 0.582 | 0.522 | 0.303 | 1.00 | 2.5s |
| 13 | Forward vs inverse kinematics | 0.441 | 0.321 | 0.232 | 0.60 | 5.3s |
| 14 | SLAM approaches | 0.403 | 0.349 | 0.224 | 0.60 | 6.6s |
| 15 | MoveIt Servo for real-time control | 0.706 | 0.521 | 0.475 | 0.60 | 3.0s |
| 16 | Narrow passage problem | 0.429 | 0.325 | 0.203 | 0.40 | 3.5s |
| 17 | ros2_control framework | 0.624 | 0.447 | 0.331 | 0.60 | 3.6s |
| 18 | Franka Panda vs UR5e | 0.444 | 0.270 | 0.211 | 1.00 | 8.3s |
| 19 | Configuration space | 0.735 | 0.679 | 0.459 | 0.80 | 4.3s |
| 20 | Nav2 for mobile navigation | 0.560 | 0.444 | 0.237 | 0.40 | 6.2s |

#### User Experience

The application provides a responsive, intuitive interface:
- **Chat-style interaction**: Users type questions naturally and receive formatted answers.
- **Example questions**: New users can click pre-populated example questions to get started immediately.
- **Source transparency**: Every answer includes an expandable "Source Documents" section showing the exact retrieved passages, allowing users to verify claims.
- **Response time display**: Each answer shows how long it took to generate.
- **Dark theme**: A modern, eye-friendly dark theme reduces visual fatigue during extended use.

---

## 7. Deployment Strategy

### Deployment Platform: Streamlit Cloud

The application is deployed on **Streamlit Cloud**, a free hosting platform purpose-built for Streamlit applications.

**Deployed Application Link:** *(to be inserted after deployment)*

### Deployment Process

1. The complete project (including the pre-built ChromaDB vector store) is pushed to a public GitHub repository.
2. On Streamlit Cloud (share.streamlit.io), the repository is connected and `app.py` is set as the main file.
3. The `OPENAI_API_KEY` is added as a secret in the Streamlit Cloud dashboard (Settings → Secrets).
4. Streamlit Cloud automatically installs dependencies from `requirements.txt` and launches the app.

### Why Streamlit Cloud

| Feature | Benefit |
|---------|---------|
| **Always on** | No sleep/wake cycle — the app loads instantly when the link is visited |
| **Free tier** | No cost for public apps |
| **Persistent URL** | The deployment link remains active indefinitely |
| **Automatic deploys** | Pushes to the GitHub repository trigger automatic redeployment |
| **Secrets management** | API keys are stored securely and injected at runtime |

### Expected User Interaction

1. User opens the deployment link in any web browser.
2. The app loads with a welcome screen showing example questions.
3. User types a robotics question or clicks an example.
4. Within 3–5 seconds, a grounded answer with source citations appears.
5. User can expand the "Source Documents" section to verify claims.
6. The conversation history is maintained within the session.

---

## 8. Expected Outcomes and Challenges

### Expected Outcomes

1. **Grounded, cited answers**: The application provides technically accurate answers grounded in verified documentation, with source citations that users can verify.
2. **Demonstrated RAG effectiveness**: The evaluation shows a **153% improvement in ROUGE-1** (0.5013 vs. 0.1978) and a **155% improvement in Token F1** (0.2683 vs. 0.1053) compared to the standalone LLM baseline, confirming that RAG grounding dramatically improves answer quality in specialized domains.
3. **Responsive user experience**: Average response time of 4.85 seconds provides a conversational interaction that is faster than manual document searching.
4. **Accessible deployment**: The application runs on Streamlit Cloud (free hosting) with OpenAI API costs under $2 total.

### Challenges Encountered and Solutions

| Challenge | Impact | Solution |
|-----------|--------|----------|
| **Initial API choice (Gemini free tier)** | Google Gemini's free tier had severe rate limits: 20 generation requests/day, 100 embedding requests/minute. This made development, evaluation, and reliable deployment impractical. | Switched to OpenAI GPT-4o-mini and text-embedding-3-small, which offer generous rate limits at extremely low cost (~$2 total for the entire project). |
| **Knowledge base coverage** | A RAG system is only as good as its knowledge base. Gaps in documentation would lead to "I don't know" responses or poor retrieval. | Authored comprehensive, factually accurate knowledge base documents covering 8 key topics in robotics and motion planning, totaling approximately 15,000 words. |
| **Chunk boundary issues** | Relevant information that spans two chunks might be split, causing incomplete retrieval. | Used overlapping chunks (100-token overlap) and semantic separators (heading boundaries, section breaks) to minimize information loss at chunk boundaries. |
| **Deployment memory constraints** | Streamlit Cloud's free tier has a 1 GB memory limit. Loading large local ML models would exceed this. | Used OpenAI's cloud-based embedding API instead of a local embedding model, eliminating the need for PyTorch on the server. The application uses only 339 MB of memory. |
| **Evaluation rigor** | Ensuring the evaluation fairly measures both RAG and baseline performance. | Designed 20 diverse benchmark questions with hand-written reference answers and relevance keywords. Ran both RAG and no-RAG baseline on the same questions for direct comparison. |

---

## 9. Resources Required

### Software and Frameworks

| Resource | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Programming language |
| Streamlit | ≥1.32.0 | Web application framework |
| LangChain | ≥0.3.0 | RAG orchestration |
| langchain-openai | ≥0.3.0 | OpenAI API integration |
| langchain-chroma | ≥0.2.0 | ChromaDB integration |
| ChromaDB | ≥0.5.0 | Vector database |
| openai | ≥1.30.0 | OpenAI API client |
| rouge-score | ≥0.1.2 | ROUGE metrics |
| scikit-learn | ≥1.4.0 | Machine learning utilities |
| psutil | ≥5.9.0 | Memory monitoring |
| python-dotenv | ≥1.0.0 | Environment variable management |

### Models (accessed via API, no local download)

- OpenAI GPT-4o-mini — text generation
- OpenAI text-embedding-3-small — vector embeddings

### Data Sources (curated knowledge base)

- Motion planning algorithms (RRT, RRT\*, PRM, STOMP, CHOMP, TrajOpt)
- MoveIt 2 framework documentation
- ROS 2 fundamentals and architecture
- Robot manipulation and grasping techniques
- Robot kinematics and dynamics
- Path planning fundamentals
- SLAM and perception for robotics
- Common robot platforms (Franka Panda, UR5e, KUKA iiwa, etc.)

### Hardware and Cost

- **Development**: Any machine with Python 3.10+ and internet access
- **Deployment**: Streamlit Cloud free tier (1 GB RAM, shared CPU) — no GPU required
- **API cost**: Under $2 total for the entire project lifecycle (development + evaluation + deployment)

---

## 10. Conclusion

### Key Takeaways

RoboRAG demonstrates that Retrieval-Augmented Generation is an effective approach for building domain-specific question-answering systems in technical fields. By grounding LLM responses in curated, verified documentation, the system provides accurate, cited answers that users can trust and verify — addressing the fundamental hallucination problem that limits the usefulness of standalone LLMs in specialized domains.

The project achieved its core objectives:

1. **Functional web application**: A responsive Streamlit chat interface that answers robotics questions with cited sources, deployed on Streamlit Cloud with a persistent URL.
2. **Quantified RAG advantage**: The full 20-question evaluation with baseline comparison demonstrates a **153% improvement in ROUGE-1** and **155% improvement in Token F1** when using RAG versus the standalone LLM, proving that retrieval grounding is essential for domain-specific accuracy.
3. **Strong retrieval quality**: Precision@5 of 77.0% confirms that the embedding model and chunking strategy effectively identify relevant knowledge base passages.
4. **Efficient and accessible**: Average latency of 4.85 seconds, memory usage of 339 MB, and total API cost under $2 make the system practical for real-world use.

### Potential Improvements and Future Enhancements

1. **Expanded knowledge base**: Incorporate additional sources — live scraping of MoveIt 2 and ROS 2 documentation, more arXiv papers, and community Q&A threads — to increase coverage and improve retrieval precision.
2. **Hybrid retrieval**: Combine dense (embedding-based) retrieval with sparse (BM25) retrieval for better handling of specific technical terms and function names.
3. **Conversational memory**: Add multi-turn conversation support where follow-up questions can reference previous answers (e.g., "Can you explain that planner in more detail?").
4. **User feedback loop**: Allow users to rate answers and flag incorrect responses, enabling iterative improvement of the knowledge base and prompt template.
5. **Fine-tuned embeddings**: Train or fine-tune an embedding model on robotics text to improve retrieval of domain-specific terminology like "configuration space" or "inverse kinematics."
6. **Upgraded LLM**: Test with GPT-4o or newer models to see if generation quality improves further, especially for complex multi-part questions.

---

## References

1. P. Lewis et al., "Retrieval-augmented generation for knowledge-intensive NLP tasks," NeurIPS, 2020.
2. A. Q. Jiang et al., "Mistral 7B," arXiv:2310.06825, 2023.
3. L. E. Kavraki, P. Svestka, J.-C. Latombe, and M. H. Overmars, "Probabilistic roadmaps for path planning in high-dimensional configuration spaces," IEEE Trans. Robotics and Automation, vol. 12, no. 4, pp. 566–580, 1996.
4. S. M. LaValle, "Rapidly-exploring random trees: A new tool for path planning," Iowa State University, Tech. Rep. TR 98-11, 1998.
5. S. Karaman and E. Frazzoli, "Sampling-based algorithms for optimal motion planning," Intl. J. Robotics Research, vol. 30, no. 7, pp. 846–894, 2011.
6. K. M. Lynch and F. C. Park, Modern Robotics: Mechanics, Planning, and Control, Cambridge Univ. Press, 2017.
7. LangChain, https://github.com/langchain-ai/langchain, 2023.
8. Chroma, https://github.com/chroma-core/chroma, 2023.
9. OpenAI API Documentation, https://platform.openai.com/docs, 2024.
10. Streamlit Documentation, https://docs.streamlit.io/, 2024.
