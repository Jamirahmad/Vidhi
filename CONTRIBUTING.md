# Contributing to Vidhi

Thank you for your interest in contributing to **Vidhi** 🎉  
Vidhi is a capstone project focused on building an **agent-based legal research and document drafting assistant** for the Indian legal ecosystem.

We welcome contributions in the form of code, documentation, bug fixes, architecture improvements, and testing.

---

## 📌 How to Contribute

You can contribute by:

- Fixing bugs or improving reliability
- Adding new agents or improving agent prompts
- Improving retrieval quality (RAG pipelines, chunking, embeddings)
- Adding document templates (petition, bail, notices, affidavits)
- Enhancing evaluation and monitoring modules
- Improving documentation, diagrams, and examples
- Adding unit tests and integration tests

---

## 🏗 Repository Structure Overview

Key directories (may expand over time):

- `src/` → core implementation of orchestrator + agents
- `agents/` → agent logic and prompt templates
- `data/` → sample datasets and metadata
- `pipelines/` → ingestion + retrieval pipelines
- `notebooks/` → experiments and prototype notebooks
- `tests/` → automated test cases
- `docs/` → diagrams, design docs, and reports

---

## ⚙️ Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/vidhi.git
cd vidhi
```
### 2. Create Virtual Environment
```bash
python -m venv venv
```
Activate:

#### Windows
```bash
venv\Scripts\activate
```
#### Linux/Mac
```bash
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Running the Project (Local)
### Run Orchestrator (Example)
```bash
python src/main.py
```

### Run a Specific Agent (Example)
```bash
python src/agents/clsa_case_law_search.py
```

## 🧠 Contribution Guidelines
### Agent Development Rules
When adding or modifying agents, ensure:
- Each agent has one clear responsibility
- Input/Output formats are strictly defined
- Agent output must be structured JSON
- Citations should be preserved wherever possible
- Each agent includes a human handoff rule
- Avoid overlapping responsibilities between agents

---

## 📄 Prompt & Output Standards
### Prompt Principles
- Keep prompts deterministic and aligned to legal domain needs
- Include formatting rules (JSON-only, headings, citations)
- Avoid hallucination-friendly phrasing like “assume” or “make up”
- Always instruct agents to respond with "NOT FOUND" if uncertain

### Output Expectations
Agents must return:
- `summary`
- `citations` (if applicable)
- `confidence_score`
- `warnings` (if any)
- `handoff_required` (true/false)
