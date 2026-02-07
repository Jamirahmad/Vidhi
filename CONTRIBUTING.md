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

---

## 🧪 Testing Guidelines
Before submitting a PR:
### Run Unit Tests
```bash
pytest
```
### Recommended Additions
- Add test cases for every new agent
- Add test cases for retrieval pipeline changes
- Validate JSON output schema in tests

---

## 📝 Documentation Standards
If your contribution changes functionality:
- Update `README.md`
- Update `CHANGELOG.md`
- Add/Update diagrams under `docs/diagrams/`
- Add sample outputs in `docs/examples/`

## 🔐 Ethics & Responsible Contribution
Vidhi supports legal workflows but must remain ethical and responsible.

Contributors must ensure:
- No features provide misleading legal advice
- No fabricated citations or false judgments are generated
- The system encourages human verification
- Data ingestion respects licensing and terms of use

---

## 🛠 Branching Strategy
Recommended workflow:

- `main` → stable branch
- `dev` → active development
- `feature/<feature-name>` → feature branches
- `bugfix/<bug-name>` → bug fix branches
Example:
```bash
git checkout -b feature/new-agent-laf
```

---

## ✅ Pull Request (PR) Process
### Step-by-Step
1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Push to your fork
5. Open a Pull Request

### PR Checklist
Your PR should include:
- [ ] Clear description of what was added/changed
- [ ] No breaking changes unless discussed
- [ ] Updated documentation (if needed)
- [ ] Updated tests (if needed)
- [ ] Updated CHANGELOG.md
- [ ] Outputs validated (JSON structure correct)

---

## ✍️ Commit Message Guidelines
Use simple and meaningful commit messages:

Examples:
- `feat: add limitation analyzer agent (LAA)`
- `fix: improve citation extraction for CLSA`
- `docs: update deployment diagram`
- `test: add retrieval precision tests`

---

## 🐛 Reporting Bugs
Please open a GitHub Issue with:
- Expected behavior
- Actual behavior
- Steps to reproduce
- Logs / error traces
- Screenshots (if applicable)

---

## 💡 Suggesting Enhancements
Enhancement proposals are welcome.

For new agents, please include:
- Agent purpose
- Inputs/outputs
- Example use case
- Expected benefit
- Potential risks (hallucination, compliance)

---

## 📜 License
By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## 🙏 Acknowledgements
Thank you for helping improve Vidhi.
Your contributions make the system more reliable, ethical, and impactful for the legal ecosystem.
