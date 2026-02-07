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
