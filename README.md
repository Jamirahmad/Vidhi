# Vidhi — Legal Case Research & Document Automation

**Vidhi** is an assistive legal research and document automation platform for the Indian legal ecosystem. It helps lawyers, litigants, and legal researchers efficiently discover relevant case laws, statutes, and judicial precedents, and generate draft legal documents with verifiable citations and human verification.

---

## Problem Statement

India’s legal system has a backlog of over 4.5 crore cases, causing delays and inefficiencies. Junior lawyers and litigants spend 40–60 hours manually reviewing case laws, precedents, and statutes. Drafting petitions, legal notices, and responses often relies on outdated templates and incomplete research, making the process slow, error-prone, and costly.

---

## Solution Overview

Vidhi assists legal professionals by automating research and drafting workflows **without replacing human judgment**. Key capabilities include:

- Retrieval of relevant case laws and statutes across Supreme Court, High Courts, and tribunals.
- Identification of legal issues, supporting and contradictory precedents, and limitation analysis.
- Drafting legal documents such as bail applications, civil suits, notices, and affidavits.
- Court-specific compliance checks and citation formatting.
- Multilingual support (English, Hindi, regional languages).
- Human-in-the-loop verification for ethical and accurate outputs.

---

## Technical Architecture

Vidhi is a **multi-agent system**, where each agent has a clear responsibility:

| Agent Name | Function / Offering |
|------------|-------------------|
| **LegalOrchestrator** | Central workflow manager; coordinates all agents and user interactions |
| **CaseFinder** | Searches relevant case laws and judicial precedents across courts |
| **IssueSpotter** | Identifies legal issues, IPC/CrPC/CPC sections, and key facts |
| **LimitationChecker** | Checks limitation periods and time-bar applicability (e.g., Section 18) |
| **ArgumentBuilder** | Builds supporting and counter-arguments based on precedents |
| **DocComposer** | Drafts petitions, notices, affidavits, and other legal documents |
| **ComplianceGuard** | Validates filings, annexures, court formatting, and fees |
| **AidConnector** | Suggests legal aid or pro-bono options for users when applicable |

---

### Technology Stack

- **Python & Jupyter Notebooks** – Core development environment  
- **LangChain / CrewAI / AutoGen** – Agent orchestration  
- **ChromaDB / FAISS** – Vector-based case retrieval  
- **OpenAI embeddings & tokenization tools** – Semantic similarity  
- **Streamlit / FastAPI / HuggingFace Spaces** – Deployment and UI  
- **LangSmith / PromptLayer** – Logging, tracing, and evaluation  
- **Translation libraries** – Multilingual document handling  

---

## Key Offerings

1. **Efficient Legal Research** – Quickly find precedents and statutes  
2. **Document Drafting** – Generate petitions, notices, and affidavits  
3. **Compliance & Verification** – Court-specific formatting, annexures, and human review  
4. **Multi-lingual Support** – English, Hindi, and regional languages  
5. **Scenario Simulation** – Test workflows for bail, civil disputes, etc.  
6. **Ethical Boundaries** – No legal opinions or fabricated cases  

---

## Limitations / Non-Goals

- Vidhi **does not provide legal advice**.  
- Cannot guarantee legal outcomes.  
- Cannot replace lawyers or court representation.  
- Novel legal questions without precedents require human review.  
- Users are responsible for filings and legal actions.  

---

## Getting Started

### Prerequisites
- Python 3.9+  
- Jupyter Notebook / VS Code  
- Libraries: `langchain`, `chromadb`, `FAISS`, `openai`, `streamlit`, `fastapi`, `requests`, `pandas`, `numpy`  

### Installation
```bash
git clone https://github.com/yourusername/vidhi.git
cd vidhi
pip install -r requirements.txt

### Usage
1. Launch the central orchestrator:
`python agents/orchestrator.py`
2. Input case facts, legal issues, and jurisdiction.
3. Workflow executes:
- CaseFinder → retrieves relevant precedents
- IssueSpotter → identifies legal issues
- LimitationChecker → evaluates time-bar
- ArgumentBuilder → generates arguments
- DocComposer → drafts legal documents
- ComplianceGuard → checks filings and formatting
- AidConnector → suggests legal aid if needed
4. Verify outputs manually before filing.

### Contributing
Contributions are welcome for improving workflows, adding legal domains, or enhancing retrieval and drafting modules.
#### Important:
- Do not generate legal opinions or fabricate case laws.
- Maintain ethical boundaries and ensure human verification for all outputs.

### License
This repository is for **educational and research purposes** only. Users are responsible for verifying all legal outputs before filing or action.

### Acknowledgements
- Indian legal system workflows and research challenges
- LangChain, CrewAI, FAISS, ChromaDB, OpenAI embeddings
- Capstone project for Indian Institute of Technology Madras - Pravartak : Agentic AI and Applications
