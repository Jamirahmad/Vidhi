# Test Philosophy – Vidhi

## Purpose of Testing

The test suite in **Vidhi** is designed to ensure that the system functions as a **reliable legal research and drafting assistant**, while strictly respecting ethical, legal, and safety boundaries.

Testing in Vidhi prioritizes:
- **Correctness over creativity**
- **Safety over automation**
- **Human verification over autonomy**

The goal is not just to validate code, but to **prevent legal harm**, hallucinated outputs, and unethical behavior.

---

## Core Testing Principles

### 1. Deterministic and Auditable
All tests are deterministic and reproducible.  
Each evaluation claim made in documentation is backed by a **named, executable test file**.

There are:
- No hidden heuristics
- No unverifiable metrics
- No silent failures

---

### 2. Agent-Centric Validation

Each agent is tested **independently** to validate:
- Input interpretation
- Output correctness
- Responsibility boundaries

This ensures agents do not overstep their intended role.

| Agent | Test File |
|-----|----------|
| IssueSpotter | `test_lii_agent.py` |
| LimitationChecker | `test_laa_agent.py` |
| CaseFinder | `test_clsa_agent.py` |
| LegalResearchAgent | `test_lra_agent.py` |
| ArgumentBuilder | `test_lab_agent.py` |
| DocComposer | `test_dga_agent.py` |
| ComplianceGuard | `test_cca_agent.py` |
| AidConnector | `test_laf_agent.py` |

---

### 3. Workflow-Level Safety

Beyond individual agents, Vidhi validates **end-to-end workflows**:
- Agent sequencing
- Task routing
- Session memory continuity
- Failure recovery and fallback paths

These are tested via:
- `test_orchestrator_flow.py`

---

### 4. Hallucination & Citation Safety (Critical)

Legal systems cannot tolerate fabricated information.

Mandatory tests ensure:
- No hallucinated case laws
- No fabricated citations
- All references trace back to indexed sources
- Mandatory disclaimers are present

Validated via:
- `test_citation_validator.py`

Any failure here is considered **deployment-blocking**.

---

### 5. Retrieval & RAG Evaluation

Vidhi evaluates retrieval quality using standard IR metrics:
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)

Tests validate:
- Semantic relevance
- Metadata correctness
- Chunk-to-document traceability

Test file:
- `test_vector_retrieval.py`

---

### 6. API & Integration Testing

API tests validate:
- Request/response schemas
- Error handling
- Rate limiting
- Input validation

Test file:
- `test_api_endpoints.py`

---

### 7. Performance & Free-Tier Constraints

Vidhi is designed for **free-tier deployment**.

Performance tests ensure:
- Acceptable latency (< 5–7 seconds)
- Graceful degradation under load
- No uncontrolled resource consumption

Benchmarks:
- `evaluation/latency_benchmarks.py`

---

## Human-in-the-Loop Enforcement

Automated tests explicitly verify that:
- Final legal documents require human review
- Novel legal questions trigger handoff flags
- Outputs are marked as “draft / assistive”

Vidhi never auto-approves legal actions.

---

## What We Do NOT Test

Vidhi intentionally does **not** test:
- Legal outcome predictions
- Case success probabilities
- Binding legal opinions

These are **explicitly out of scope** and must remain human-driven.

---

## Final Assurance

> Every test in this directory exists to protect users, lawyers, and institutions from incorrect or unethical legal automation.

Vidhi’s test suite is not just a quality gate —  
it is a **legal safety mechanism**.
