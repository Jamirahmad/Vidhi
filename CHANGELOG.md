# Changelog

All notable changes to **Vidhi** will be documented in this file.

This project follows **Semantic Versioning** (`MAJOR.MINOR.PATCH`) and maintains structured release notes for capstone evaluation and future industry-readiness.

---

## [Unreleased]
### Added
- 
- 
- 
- 

### Changed
- 

### Fixed
- 

### Removed
- 

---

## [0.1.0] - Feb 07, 2026
### Added
#### Project Setup & Repository Foundation
- Initialized repository structure for **Vidhi** capstone project.
- Added `README.md` covering:
  - Problem statement
  - Solution overview
  - Multi-agent architecture
  - Usage
  - Technical stack
  - Limitations
  - Contributing, License, Acknowledgements
- Added `LICENSE` placeholder for open-source distribution.
- Added `.gitignore` for Python development and notebook artifacts.

#### Multi-Agent Architecture Definition
- Finalized multi-agent roles and system naming:
  - **LII** (Issue Identifier Agent)
  - **LAA** (Limitation Analyzer Agent)
  - **CLSA** (Case Law Search Agent)
  - **LRA** (Legal Research Agent)
  - **LAB** (Legal Argument Builder Agent)
  - **DGA** (Document Generation Agent)
  - **CCA** (Compliance Check Agent)
  - **LAF** (Legal Aid Finder Agent)
- Defined orchestration design with a central **Vidhi Orchestrator**.

#### Architecture & Documentation
- Added clean multi-agent architecture diagram (box + arrow layout) for PPT use.
- Documented responsibilities, expected inputs/outputs, and human handoff logic for each agent.
- Introduced ethics and governance expectations:
  - Human verification required before legal filing
  - Non-advisory disclaimer requirements
  - Hallucination control and citation validation plan

#### Data Strategy Planning
- Identified target legal sources:
  - Supreme Court judgments
  - High Court judgments
  - Tribunal decisions (CAT, NCLT, ITAT, etc.)
- Defined ingestion plan:
  - Court portal scraping (where permitted)
  - PDF parsing pipeline
  - Text chunking and metadata tagging
  - Embedding + vector storage for retrieval

#### Deployment Strategy (Free Tier Focus)
- Defined free-tier deployment approach (local + cloud hybrid):
  - Local ingestion + embedding generation
  - Vector DB using FAISS/ChromaDB
  - Lightweight orchestration pipeline
  - Logging and monitoring plan suitable for student capstone

#### Capstone Alignment
- Ensured repository structure and documentation align with syllabus modules:
  - Agentic tools in Python
  - Agent architectures & collaboration
  - Memory & knowledge retrieval
  - Advanced RAG
  - Deployment & monitoring
  - Evaluation & debugging
  - Ethics & governance

### Changed
- Refined naming conventions to avoid explicitly mentioning "AI" in branding.
- Improved clarity of system boundaries between:
  - Retrieval layer
  - Agent reasoning layer
  - Document drafting layer
  - Compliance validation layer

### Fixed
- Corrected agent role overlap by separating:
  - Search vs research synthesis responsibilities
  - Drafting vs compliance responsibilities

### Removed
- Removed generic tool references not aligned with syllabus-driven approach.

---
