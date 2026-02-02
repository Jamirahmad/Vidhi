# Vidhi — Legal Case Research & Document Automation

**Vidhi** is an assistive legal research and document automation platform designed to help lawyers, litigants, and legal researchers efficiently discover relevant case laws, statutes, and judicial precedents, and generate draft legal documents grounded in verifiable citations.

---

## Problem Statement

The Indian legal system faces a backlog of over 4.5 crore cases, causing delays and inefficiencies in research and documentation. Junior lawyers and litigants often spend 40–60 hours manually reviewing case laws, precedents, and legal statutes. Existing solutions are costly, and manual research is error-prone, incomplete, and time-consuming. Drafting petitions, legal notices, and responses often relies on outdated templates and lacks comprehensive legal references.

---

## Solution Overview

Vidhi aims to **assist legal professionals and litigants** by automating the research and drafting workflow, without replacing human judgment. It provides:

- Autonomous retrieval of relevant case laws and statutes across Supreme Court, High Courts, and tribunals.
- Identification of legal issues, supporting and contradictory precedents, and limitation analysis.
- Drafting of legal documents such as bail applications, civil suits, legal notices, and affidavits.
- Court-specific compliance checks and citation formatting.
- Multilingual support for English, Hindi, and regional languages.
- Human-in-the-loop verification to ensure ethical, safe, and accurate outputs.

---

## Technical Solution / Architecture

Vidhi is built as a **multi-agent system**, where each agent has a distinct responsibility:

| Agent | Function |
|-------|---------|
| **LRA (Legal Research Agent)** | Orchestrates tasks across all sub-agents and handles user interaction |
| **CLSA (Case Law Search Agent)** | Retrieves relevant case laws and judicial precedents |
| **LII (Legal Issue Identifier)** | Extracts legal issues, IPC/CrPC/CPC sections, and key facts from input |
| **LAA (Limitation Analysis Agent)** | Determines limitation applicability based on case facts |
| **LAB (Legal Argument Builder)** | Constructs supporting and counter-arguments using precedents |
| **DGA (Document Generation Agent)** | Drafts legal documents with court-specific formatting |
| **CCA (Compliance Check Agent)** | Validates filings, annexures, affidavits, and court fees |
| **LAF (Legal Aid Finder)** | Suggests legal aid or pro-bono options if needed |

**Technical Stack:**

- **Python & Jupyter Notebooks** – Core language and development environment  
- **LangChain / CrewAI / AutoGen** – Agent orchestration and workflow management  
- **ChromaDB / FAISS** – Vector-based retrieval of legal documents  
- **OpenAI embeddings & tokenization tools** – Text embeddings and semantic similarity  
- **Streamlit / FastAPI / HuggingFace Spaces** – Deployment and UI  
- **LangSmith / PromptLayer** – Logging, tracing, and evaluation  
- **Translation libraries** – Multilingual document handling  

---

## Key Offerings

1. **Efficient Legal Research** – Quickly find relevant precedents and statutes.  
2. **Document Drafting** – Generate petitions, notices, and affidavits with proper citations.  
3. **Compliance & Verification** – Court-specific formatting, annexures, and human-in-the-loop checks.  
4. **Multi-lingual Support** – Supports English, Hindi, and regional languages.  
5. **Scenario Simulation** – Test workflows for bail, civil disputes, or other case types.  
6. **Ethical Boundaries** – Prevents generation of legal opinions or fabricated case laws.

---

## Limitations / Non-Goals

- Vidhi **does not provide legal opinions or advice**.  
- Cannot guarantee case outcomes or success in court.  
- Does not replace lawyers or human judgment in filing or court representation.  
- Novel legal questions without precedents require human analysis.  
- Filing of documents and legal representation remains the user’s responsibility.

---

## Getting Started

### Prerequisites
- Python 3.9+  
- Jupyter Notebook / VS Code  
- Required libraries: `langchain`, `chromadb`, `FAISS`, `openai`, `streamlit`, `fastapi`, `requests`, `pandas`, `numpy`  

### Installation
```bash
git clone https://github.com/yourusername/vidhi.git
cd vidhi
pip install -r requirements.txt

