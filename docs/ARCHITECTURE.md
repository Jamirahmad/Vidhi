# Vidhi — System Architecture

Vidhi is a **multi-agent legal research and document automation platform** designed for the Indian legal ecosystem. It assists lawyers, litigants, and legal researchers in discovering relevant case laws, statutes, and judicial precedents, and generating structured draft legal documents with **verifiable citations** and **human verification**.

Vidhi is built as a modular, agent-driven system where each agent performs a specialized responsibility (research, issue spotting, limitation analysis, drafting, compliance validation, etc.) while a central orchestrator coordinates execution and ensures ethical and safe outputs.

This document provides a **high-level architecture overview** and references the detailed design documents and diagrams stored under the `/docs` folder.

---

## Architecture Goals

Vidhi’s architecture is designed to ensure:

- **Separation of responsibilities** across specialized agents  
- **Traceability and explainability** via citations and structured outputs  
- **Human-in-the-loop validation** for legal and ethical safety  
- **Pluggable ingestion + retrieval pipelines** (SC, HC, Tribunals, user uploads)  
- **Scalable deployment options**, including free-tier compatible setups  
- **Evaluation and monitoring** for hallucination detection and citation accuracy  

---

## High-Level System Components

Vidhi is composed of the following major subsystems:

### 1. User Interaction Layer
- Streamlit UI for interactive legal case intake and reporting
- FastAPI layer for programmatic access and future integration

### 2. Orchestration Layer
- Central orchestrator coordinates tasks and delegates to agents
- Task router ensures correct execution ordering
- Response formatter produces structured output suitable for review

### 3. Multi-Agent Execution Layer
- Specialized agents for legal research, drafting, compliance checks, and legal aid suggestions
- Agents communicate through orchestrator-managed structured inputs/outputs

### 4. Retrieval & Knowledge Layer (RAG)
- Embedding pipeline converts legal text into vector representations
- Vector store enables similarity-based retrieval (ChromaDB/FAISS)
- Retriever + reranker ensures relevant precedents are returned

### 5. Data Ingestion Pipeline
- Fetchers scrape or pull content from legal sources (SC, HC, tribunals)
- Parsers extract clean text from PDFs/HTML/OCR outputs
- Chunking breaks content into retrieval-friendly segments
- Metadata extraction ensures documents remain traceable and auditable

### 6. Governance & Safety Layer
- Safety guardrails prevent unsafe output generation
- Citation validation ensures references are real and consistent
- Human handoff rules enforce review before legal usage

### 7. Evaluation & Monitoring Layer
- Automated test suites for citation accuracy and hallucination checks
- Latency benchmarking and workflow validation
- Trace logs for debugging agent decisions

---

## Multi-Agent Architecture Overview

Vidhi uses a **multi-agent architecture**, where each agent has a single primary responsibility and communicates through well-defined input/output formats.

The orchestrator ensures:
- deterministic task execution order
- safe prompt handling
- structured outputs
- audit-friendly traceability

### Core Agents (Functional Roles)

| Agent Code | Agent Name | Responsibility |
|-----------|------------|----------------|
| **LRA** | Legal Research Agent | Overall research planning and research synthesis |
| **CLSA** | Case Law Search Agent | Retrieves relevant case laws, judgments, precedents |
| **LII** | Legal Issue Identifier | Extracts legal issues, sections, and key dispute points |
| **LAA** | Limitation Analysis Agent | Checks limitation/time-bar rules applicability |
| **LAB** | Legal Argument Builder | Builds supporting and counter-arguments using precedents |
| **DGA** | Document Generation Agent | Drafts petitions, notices, affidavits, legal responses |
| **CCA** | Compliance Check Agent | Checks formatting, annexures, jurisdiction compliance |
| **LAF** | Legal Aid Finder | Suggests legal aid/pro-bono options when applicable |

For detailed responsibilities, refer to:
- [`docs/design/agent_responsibilities.md`](./design/agent_responsibilities.md)

---

## Architecture Diagrams (Reference)

All system diagrams are stored in the `/docs/architecture/` directory.

### 1. Multi-Agent Architecture Diagram
Shows how the orchestrator interacts with all agents and shared services.

- Diagram: `docs/architecture/multi_agent_architecture.png`

### 2. User Workflow Sequence Diagram
Shows end-to-end workflow from case intake to final output generation.

- Diagram: `docs/architecture/sequence_diagram_user_flow.png`

### 3. Data Ingestion Pipeline Diagram
Shows ingestion flow from data sources to processed vector store.

- Diagram: `docs/architecture/data_ingestion_pipeline.png`

### 4. Deployment Diagram (Free Tier)
Shows deployment using free-tier compatible infrastructure (local / AWS / Streamlit Cloud).

- Diagram: `docs/architecture/deployment_free_tier.png`

---

## End-to-End Workflow (Execution Flow)

Vidhi executes the following high-level workflow:

### Step 1: User Input (Case Intake)
User provides:
- Case facts
- Jurisdiction (State / Court)
- Case type (civil/criminal/tribunal)
- Relevant legal issues (optional)

### Step 2: Orchestrator Planning
The orchestrator:
- validates inputs
- identifies workflow path based on case type
- determines which agents to invoke
- initializes memory/session state

### Step 3: Research & Retrieval
Agents invoked:
- **CLSA** retrieves relevant case laws, judgments, statutes
- **LRA** synthesizes retrieved results into structured research notes

### Step 4: Legal Understanding
Agents invoked:
- **LII** identifies legal issues and applicable sections (IPC/CrPC/CPC/etc.)
- **LAA** checks limitation/time-bar applicability

### Step 5: Argument Development
Agents invoked:
- **LAB** builds arguments and counter-arguments
- output includes precedent-backed reasoning

### Step 6: Draft Generation
Agents invoked:
- **DGA** generates a draft legal document aligned to templates

### Step 7: Compliance Validation
Agents invoked:
- **CCA** checks formatting, annexures, filing compliance, jurisdiction constraints

### Step 8: Legal Aid Suggestions (Optional)
Agents invoked:
- **LAF** suggests legal aid/pro-bono options (if relevant)

### Step 9: Human Review & Final Output
Final output is packaged into:
- Research Report
- Draft Document
- Compliance Checklist
- Citation References

All outputs are returned for **human verification** and lawyer review.

---

## Retrieval-Augmented Generation (RAG) Architecture

Vidhi uses RAG to ensure legal outputs are grounded in real case law and citations.

### RAG Workflow

1. **Query Formation**
   - Orchestrator creates a legal search query from case facts and issues

2. **Embedding**
   - Query is converted into vector representation using embedding provider

3. **Vector Search**
   - FAISS/ChromaDB retrieves top-N most relevant chunks

4. **Reranking**
   - Optional reranking improves relevance ordering

5. **Citation-Linked Context Assembly**
   - Retrieved chunks are packaged with metadata (court, date, citation ID)

6. **Agent Prompt Injection**
   - Context is passed to agents for reasoning and drafting

7. **Citation Validation**
   - Output citations are checked against metadata store

---

## Key Design Principles

### 1. Human-in-the-Loop is Mandatory
Vidhi is designed to assist, not replace.
Every draft must be reviewed by a qualified legal professional.

### 2. Citation First Approach
All research outputs must include:
- court name
- case name
- year
- citation / identifier (if available)
- retrieved excerpt

### 3. Modular Agent Responsibilities
Each agent has:
- a single responsibility
- clear input/output schema
- isolated prompts and templates

### 4. Safety Guardrails by Default
The system prevents:
- legal advice generation
- fabricated citations
- unsafe instructions
- false authority claims

For detailed safety policy, refer to:
- [`docs/design/safety_ethics_governance.md`](./design/safety_ethics_governance.md)

---

## Storage and Persistence Design

Vidhi persists data across layers:

### Raw & Processed Data
Stored under:
- `data/raw/`
- `data/processed/`
- `data/chunks/`

### Vector Stores
Stored under:
- `vectorstore/faiss_index/`
- `vectorstore/chroma_db/`

### Outputs
Stored under:
- `outputs/research_reports/`
- `outputs/generated_documents/`
- `outputs/compliance_reports/`
- `outputs/evaluation_results/`

### Logs
Stored under:
- `logs/app.log`
- `logs/retrieval.log`
- `logs/agent_traces.log`

---

## Human Handoff Rules

Human review is enforced at critical stages:

- After retrieval synthesis (confirm relevance)
- After argument building (validate reasoning and applicability)
- After draft generation (ensure correctness and intent)
- After compliance checks (confirm jurisdiction requirements)

For complete handoff rules, refer to:
- [`docs/design/human_handoff_rules.md`](./design/human_handoff_rules.md)

---

## Deployment Architecture (Free-Tier Friendly)

Vidhi supports deployment across:

- **Local Docker Compose** (recommended for capstone evaluation)
- **AWS Free Tier EC2 + S3**
- **Streamlit Cloud / HuggingFace Spaces**
- **Render / Replit (lightweight prototype deployment)**

For details, refer to:
- `docs/architecture/deployment_free_tier.png`
- `deployments/aws_free_tier/`
- `deployments/local/docker-compose.yml`

---

## Evaluation and Observability

Vidhi includes built-in evaluation support:

- citation accuracy testing
- hallucination detection checks
- latency benchmarking
- rubric-based scoring aligned to capstone expectations

For evaluation details, refer to:
- [`docs/design/evaluation_strategy.md`](./design/evaluation_strategy.md)

---

## Related Documentation Index

This file is intended as the architecture entrypoint. The following documents provide deeper details:

### Design Documents
- [`docs/design/problem_statement.md`](./design/problem_statement.md)
- [`docs/design/scope_and_boundaries.md`](./design/scope_and_boundaries.md)
- [`docs/design/agent_responsibilities.md`](./design/agent_responsibilities.md)
- [`docs/design/human_handoff_rules.md`](./design/human_handoff_rules.md)
- [`docs/design/safety_ethics_governance.md`](./design/safety_ethics_governance.md)
- [`docs/design/evaluation_strategy.md`](./design/evaluation_strategy.md)
- [`docs/design/limitations.md`](./design/limitations.md)

### Dataset and Ingestion
- [`docs/dataset/data_sources.md`](./dataset/data_sources.md)
- [`docs/dataset/ingestion_strategy.md`](./dataset/ingestion_strategy.md)
- [`docs/dataset/sample_dataset_manifest.md`](./dataset/sample_dataset_manifest.md)

### API Documentation
- [`docs/api/openapi_spec.yaml`](./api/openapi_spec.yaml)
- [`docs/api/api_examples.md`](./api/api_examples.md)

---

## Disclaimer

Vidhi is a research and drafting assistant.  
It does not provide legal advice, and all outputs must be reviewed and validated by a qualified legal professional before use.

This system is designed for educational and research purposes as part of a capstone project.
