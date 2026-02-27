
# NexaSupport: Enterprise-Grade RAG & Agentic Orchestrator

**NexaSupport** is an intelligent AI agent designed to bridge the gap between unstructured corporate knowledge (PDFs, docs) and structured enterprise workflows (IT, HR, and DevOps). Built for the **Kshitij 2026** competition, this system demonstrates how a Large Language Model (LLM) can act as a "Brain" to not only answer questions but also execute complex cross-domain tasks.

---

## 1. Core Concepts

### **Retrieval-Augmented Generation (RAG)**

Standard LLMs are limited to their training data. **RAG** allows this agent to "look up" specific, private information—like the **HCLTech Annual Report 2024-25**—before generating an answer. It retrieves the most relevant text chunks from a vector database, ensuring that responses are grounded in fact and cited with page numbers, effectively eliminating hallucinations.

### **Tool Orchestration**

Instead of just chatting, the agent uses **ReAct (Reason + Act)** logic. When a user asks a complex query, the agent evaluates which "tools" it needs to use. It can chain multiple actions together—such as checking a GitHub repo's health, booking a deployment slot, and verifying a network status—all in a single conversation turn.

---

## 2. The Tech Stack

| Layer | Technology |
| --- | --- |
| **Brain (LLM)** | **Gemini 2.0 Flash** (via Google AI Studio) |
| **Embedding Model** | **BGE-M3** (Multi-Lingual, Multi-Function, Multi-Granularity) |
| **Vector Database** | **Milvus** (Hybrid search with Dense & Sparse vectors) |
| **Orchestration** | **LangChain** (AgentExecutor & Custom Tool Decorators) |
| **UI / Frontend** | **Streamlit** (Custom CSS for Enterprise Branding) |
| **Data Processing** | **PyPDF** (Metadata-aware parsing) & **RecursiveCharacterTextSplitter** |

---

## 3. What Are We Doing?

NexaSupport solves the problem of "Information Silos" in a corporate environment. We have integrated four distinct domains into one unified interface:

1. **Financial/Corporate Intelligence**: The agent performs hybrid semantic search across the 400+ page HCLTech Annual Report to extract revenue, risks, and strategic goals.
2. **DevOps Integration**: It connects to simulated GitHub environments to check repository vulnerabilities and book deployment windows via a custom Jenkins-style interface.
3. **HR & Benefits Management**: It cross-references internal employee databases (JSON) with benefits policies (TXT) to provide personalized leave balance checks and reimbursement validations.
4. **IT Infrastructure Monitoring**: It monitors real-time system health and network status (e.g., Singapore office outages) and can autonomously file high-priority IT support tickets.

### **Key Feature: Multilingual Intelligence**

By utilizing the **BGE-M3** model, the agent supports **Cross-Lingual Retrieval**. You can ask a question in Hindi (e.g., *"HCLTech का राजस्व क्या था?"*), and the agent will accurately retrieve the answer from the English-language PDF.

---

## ⚙️ Setup & Installation

1. **Clone the repo:**
```bash
git clone https://github.com/agarwalmaanvik/NLP.git

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Configure Environment:**
Create a `.env` file with your `GOOGLE_API_KEY`.
4. **Ingest Data:**
```bash
python ingest.py

```


5. **Run the App:**
```bash
streamlit run app.py

```



---

**Next Step:** Once you’ve pushed this to GitHub, would you like me to help you draft a **"Judge’s Cheat Sheet"** that lists exactly what points you should hit during the 5-minute presentation?
