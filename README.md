# Vidhi — Legal Case Research & Document Automation

**Vidhi** is an assistive legal research and document automation platform for the Indian legal ecosystem. It helps lawyers, litigants, and legal researchers efficiently discover relevant case laws, statutes, and judicial precedents, and generate draft legal documents with verifiable citations and human verification.

---

## Problem Statement

India’s legal system has a backlog of over **4.5 crore cases**, causing delays and inefficiencies. Junior lawyers and litigants spend **40–60 hours** manually reviewing case laws, precedents, and statutes.

Drafting petitions, legal notices, and responses often relies on outdated templates and incomplete research, making the process slow, error-prone, and costly.

---

## Solution Overview

Vidhi assists legal professionals by automating research and drafting workflows **without replacing human judgment**.

Key capabilities include:

- Retrieval of relevant case laws and statutes across Supreme Court, High Courts, and tribunals
- Identification of legal issues, supporting and contradictory precedents, and limitation analysis
- Drafting legal documents such as bail applications, civil suits, notices, and affidavits
- Court-specific compliance checks and citation formatting
- Multilingual support (English, Hindi, and regional languages)
- Human-in-the-loop verification for ethical and accurate outputs

---

## Technical Architecture

Vidhi is designed as a **multi-agent system**, where each agent has a clear responsibility and defined input/output contracts.

### Agent Map

| Agent Name | Function / Offering |
|------------|----------------------|
| **LegalOrchestrator** | Central workflow manager; coordinates all agents and user interactions |
| **CaseFinder** | Searches relevant case laws and judicial precedents across courts |
| **IssueSpotter** | Identifies legal issues, IPC/CrPC/CPC sections, and key facts |
| **LimitationChecker** | Checks limitation periods and time-bar applicability (e.g., Section 18) |
| **ArgumentBuilder** | Builds supporting and counter-arguments based on precedents |
| **DocComposer** | Drafts petitions, notices, affidavits, and other legal documents |
| **ComplianceGuard** | Validates filings, annexures, court formatting, and court fees |
| **AidConnector** | Suggests legal aid / pro-bono options for users when applicable |

---

## Technology Stack

This project uses tools aligned with the course syllabus for agentic AI development:

- **Python & Jupyter Notebooks** – Core development environment  
- **LangChain / CrewAI / AutoGen** – Agent orchestration and workflows  
- **ChromaDB / FAISS** – Vector storage and similarity search  
- **Embedding Models** – Semantic retrieval for case laws and statutes  
- **Streamlit / FastAPI / HuggingFace Spaces** – UI and deployment options  
- **LangSmith / PromptLayer** – Tracing, debugging, and evaluation  
- **Translation Libraries** – Multilingual drafting support (English/Hindi/Regional)

---

## Key Offerings

1. **Efficient Legal Research**  
   Retrieve case laws, precedents, and statutory provisions quickly.

2. **Document Drafting Automation**  
   Generate draft petitions, bail applications, notices, affidavits, and replies.

3. **Compliance & Verification Support**  
   Validate annexures, missing affidavits, court fee estimates, and formatting.

4. **Multi-lingual Support**  
   Translate and draft documents across English, Hindi, and regional languages.

5. **Scenario Simulation**  
   Supports workflow simulation for bail, fraud, property disputes, etc.

6. **Ethical Boundaries Built-In**  
   Human verification is mandatory; no fake case laws are allowed.

---

## Limitations / Non-Goals

Vidhi is strictly a research and drafting assistant.

- Vidhi **does not provide legal advice**
- Vidhi cannot guarantee legal outcomes
- Vidhi cannot replace lawyers or court representation
- Novel legal questions without precedents require human review
- Users are responsible for filing, signatures, and court submission
- Outputs must be verified before use in any legal proceeding

---

## Usage

### Step-by-step Workflow

1. Launch the central orchestrator:
```bash
   python agents/orchestrator.py
```
2. Provide inputs:
- Case facts
- Relevant legal issues
- Jurisdiction (State / Court)
- Case type (civil/criminal/tribunal)

3. Vidhi runs a multi-agent workflow:
- **CaseFinder** → retrieves relevant precedents
- **IssueSpotter** → identifies legal issues and applicable sections
- **LimitationChecker** → evaluates limitation/time-bar conditions
- **ArgumentBuilder** → generates arguments and counter-arguments
- **DocComposer** → drafts legal documents
- **ComplianceGuard** → checks filing requirements and formatting
- **AidConnector** → suggests legal aid options if applicable

4. Final output is returned for human verification and lawyer review.

---

## Getting Started
### Prerequisites
- Python 3.9+
- Jupyter Notebook / VS Code
- Git installed

Recommended Python libraries:
- `langchain`
- `chromadb`
- `faiss-cpu`
- `openai`
- `streamlit`
- `fastapi`
- `requests`
- `pandas`
- `numpy`

---

## Installation
```bash
git clone https://github.com/yourusername/vidhi.git
cd vidhi
pip install -r requirements.txt
```

---

## Project Structure (High-Level)
```bash
vidhi/
│
├── agents/                # All multi-agent modules
├── prompts/               # Prompt templates used by each agent
├── data/                  # Raw and processed case law datasets (local)
├── vectorstore/           # ChromaDB/FAISS persistent storage
├── docs/                  # Architecture diagrams and documentation
├── notebooks/             # Jupyter notebooks for experiments
├── tests/                 # Unit tests and evaluation scripts
├── app/                   # Streamlit / API entrypoints
│
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── requirements.txt
└── .env.example
```

---

## Contributing
Contributions are welcome for improving workflows, adding legal domains, or enhancing retrieval and drafting modules.

Please read [CONTRIBUTING.md](https://github.com/Jamirahmad/Vidhi/blob/main/CONTRIBUTING.md) before raising a pull request.

### Important Contribution Rules
- Do not generate legal opinions
- Do not fabricate case laws or citations
- Always enforce human verification
- Respect ethical boundaries and safety requirements

---

## License

This repository is for **educational and research purposes only.**

Users are responsible for verifying all legal outputs before filing or taking any legal action.

See [LICENSE](https://github.com/Jamirahmad/Vidhi/blob/main/LICENSE) for details.

---

## Acknowledgements
- Indian legal system workflows and legal research challenges
- LangChain, CrewAI, AutoGen
- FAISS, ChromaDB
- OpenAI Embeddings and tokenization tools
- Capstone project for **IIT Madras - Pravartak** Agentic AI and Applications Program

---

## Disclaimer

Vidhi is a research and drafting assistant.
It does **not** provide legal advice, and all outputs must be reviewed and validated by a qualified legal professional before use.
