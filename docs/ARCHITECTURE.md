# Vidhi — System Architecture

Vidhi is a **multi-agent legal research and document automation platform** designed for the Indian legal ecosystem. It assists lawyers, litigants, and legal researchers in discovering relevant case laws, statutes, and judicial precedents, and generating structured draft legal documents with **verifiable citations** and **human verification**.

Vidhi is built as a modular, agent-driven system where each agent performs a specialized responsibility (research, issue spotting, limitation analysis, drafting, compliance validation, etc.) while a central orchestrator coordinates execution and ensures ethical and safe outputs.

This document provides a **high-level architecture overview**, including the **multi-agent workflow**, and references the detailed design documents and diagrams stored under the `/docs` folder.

---

## Architecture Goals

Vidhi’s architecture is designed to ensure:

- Clear separation of responsibilities across specialized agents  
- Traceability and explainability via citations and structured outputs  
- Human-in-the-loop validation for legal and ethical safety  
- Pluggable ingestion + retrieval pipelines (SC, HC, Tribunals, user uploads)  
- Scalable deployment options including free-tier compatible setups  
- Evaluation and monitoring for hallucination detection and citation accuracy  

---

## Architecture Diagrams (Quick Reference)

All architecture diagrams are stored in:  
📁 `docs/architecture/`

| Diagram | Purpose | File |
|--------|---------|------|
| Multi-Agent Architecture | Shows orchestrator + all agents + shared services | `docs/architecture/multi_agent_architecture.png` |
| User Flow Sequence Diagram | End-to-end user journey from input to output | `docs/architecture/sequence_diagram_user_flow.png` |
| Data Ingestion Pipeline | Shows ingestion pipeline from sources to vector DB | `docs/architecture/data_ingestion_pipeline.png` |
| Deployment (Free Tier) | Free-tier deployment setup across AWS/local options | `docs/architecture/deployment_free_tier.png` |

---

## High-Level System Components

Vidhi is composed of the following major subsystems:

### 1. User Interaction Layer
- Streamlit UI for interactive legal case intake and reporting
- FastAPI layer for programmatic access and integration

### 2. Orchestration Layer
- Central orchestrator coordinates tasks and delegates to agents
- Task router ensures correct ordering of execution
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
- Metadata extraction ensures traceability and auditability

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

📌 Refer diagram:  
**`docs/architecture/multi_agent_architecture.png`**

---

## Multi-Agent Workflow (Explicit Flow)

This is the **end-to-end multi-agent execution flow** followed by Vidhi:

### Step 1: Case Intake (User Input)
User provides:
- Case facts
- Case type (civil / criminal / tribunal)
- Jurisdiction (State / Court)
- Optional known legal issues

---

### Step 2: Orchestrator Planning
**LegalOrchestrator**:
- validates inputs
- classifies case type
- determines workflow route
- initializes session memory
- creates a structured execution plan

---

### Step 3: Research & Precedent Retrieval
**CLSA (CaseFinder / Case Law Search Agent)**:
- searches case laws and judicial precedents
- retrieves relevant judgments from SC/HC/tribunals
- returns top-N ranked results with metadata

**LRA (Legal Research Agent)**:
- synthesizes retrieved judgments into a structured research brief
- highlights supporting vs contradictory precedents

📌 Diagram reference:  
**`docs/architecture/sequence_diagram_user_flow.png`**

---

### Step 4: Legal Issue Extraction
**LII (IssueSpotter / Legal Issue Identifier Agent)**:
- identifies legal issues
- extracts relevant IPC/CrPC/CPC/other sections
- identifies parties, timeline, and dispute structure
- tags the case domain (bail, consumer, property, service, etc.)

---

### Step 5: Limitation & Time-Bar Analysis
**LAA (LimitationChecker / Limitation Analysis Agent)**:
- checks limitation periods based on case type
- identifies time-bar risks
- flags potential condonation or exception applicability

---

### Step 6: Argument Development
**LAB (ArgumentBuilder / Legal Argument Builder Agent)**:
- generates arguments aligned to the case facts
- generates counter-arguments and risk analysis
- links each argument with supporting citations

---

### Step 7: Draft Document Generation
**DGA (DocComposer / Document Generation Agent)**:
- generates draft legal documents using templates
- includes structured sections (facts, issues, prayers, annexures)
- embeds citations where applicable

---

### Step 8: Compliance & Filing Readiness Check
**CCA (ComplianceGuard / Compliance Check Agent)**:
- validates document formatting
- checks court/jurisdiction requirements
- checks annexure checklist completeness
- ensures citations and references are consistent

---

### Step 9: Legal Aid & Support (Optional)
**LAF (AidConnector / Legal Aid Finder Agent)**:
- suggests legal aid / pro-bono resources (if needed)
- recommends legal help avenues depending on location

---

### Step 10: Final Human Handoff
Final output returned for:
- human verification
- lawyer review
- correction and refinement before filing

📌 Human Handoff Rules reference:  
**`docs/design/human_handoff_rules.md`**

---

## Agents Summary (Roles)

| Agent Code | Agent Name | Responsibility |
|-----------|------------|----------------|
| **LRA** | Legal Research Agent | Synthesizes and structures legal research |
| **CLSA** | Case Law Search Agent | Retrieves judgments and precedents |
| **LII** | Legal Issue Identifier | Identifies issues and applicable sections |
| **LAA** | Limitation Analysis Agent | Checks limitation/time-bar conditions |
| **LAB** | Legal Argument Builder | Builds arguments + counter-arguments |
| **DGA** | Document Generation Agent | Drafts petitions, notices, affidavits |
| **CCA** | Compliance Check Agent | Validates formatting and filing readiness |
| **LAF** | Legal Aid Finder Agent | Suggests legal aid/pro-bono options |

For detailed responsibilities, refer to:  
📌 `docs/design/agent_responsibilities.md`

---

## Retrieval-Augmented Generation (RAG) Architecture

Vidhi uses RAG to ensure outputs are grounded in real case law and citations.

### RAG Workflow

1. Query formation from case facts and legal issues  
2. Embedding generation using embedding provider  
3. Vector search (FAISS/ChromaDB) retrieves top-N relevant chunks  
4. Optional reranking improves relevance ordering  
5. Context is assembled with metadata (court, year, citation)  
6. Agents generate responses using retrieved context  
7. Citation validation checks outputs against stored metadata  

📌 Refer diagram:  
**`docs/architecture/data_ingestion_pipeline.png`**

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

## Deployment Architecture (Free-Tier Friendly)

Vidhi supports deployment across:

- Local Docker Compose (recommended for capstone evaluation)
- AWS Free Tier (EC2 + S3 optional)
- Streamlit Cloud / HuggingFace Spaces
- Render / Replit (lightweight prototype deployment)

📌 Refer diagram:  
**`docs/architecture/deployment_free_tier.png`**

---

## Evaluation and Observability

Vidhi includes built-in evaluation support:

- citation accuracy testing
- hallucination detection checks
- latency benchmarking
- rubric-based scoring aligned to capstone expectations

📌 Refer:  
- `docs/design/evaluation_strategy.md`
- `src/evaluation/`

---

## Related Documentation Index

This file is the architecture entrypoint. The following documents provide deeper details:

### Design Documents
- `docs/design/problem_statement.md`
- `docs/design/scope_and_boundaries.md`
- `docs/design/agent_responsibilities.md`
- `docs/design/human_handoff_rules.md`
- `docs/design/safety_ethics_governance.md`
- `docs/design/evaluation_strategy.md`
- `docs/design/limitations.md`

### Dataset and Ingestion
- `docs/dataset/data_sources.md`
- `docs/dataset/ingestion_strategy.md`
- `docs/dataset/sample_dataset_manifest.md`

### API Documentation
- `docs/api/openapi_spec.yaml`
- `docs/api/api_examples.md`

---

## Disclaimer

Vidhi is a research and drafting assistant.  
It does not provide legal advice, and all outputs must be reviewed and validated by a qualified legal professional before use.

This system is designed for educational and research purposes as part of a capstone project.
