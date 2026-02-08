
# Evaluation Strategy

## Overview
This document defines how **Vidhi** is evaluated for accuracy, safety, reliability, and ethical compliance.  
Each evaluation dimension is directly mapped to executable test cases under the `/tests` directory to ensure traceability, reproducibility, and audit readiness.

Vidhi prioritizes **legal safety over automation speed**, enforcing mandatory human verification at critical decision points.

---

## Evaluation Objectives
- Ensure factual correctness of retrieved case laws and statutes
- Prevent hallucinated citations or fabricated precedents
- Validate agent-specific responsibilities and outputs
- Measure retrieval relevance and workflow reliability
- Enforce ethical, legal, and human-in-the-loop boundaries

---

## Agent-Level Functional Accuracy

| Agent | Evaluation Focus | Test File |
|-----|------------------|----------|
| IssueSpotter (LII) | Legal issue & section identification | tests/test_lii_agent.py |
| LimitationChecker (LAA) | Limitation & revival logic | tests/test_laa_agent.py |
| CaseFinder (CLSA) | Relevant precedent discovery | tests/test_clsa_agent.py |
| LegalResearchAgent (LRA) | Research coherence | tests/test_lra_agent.py |
| ArgumentBuilder (LAB) | Arguments & counter-arguments | tests/test_lab_agent.py |
| DocComposer (DGA) | Draft quality & template use | tests/test_dga_agent.py |
| ComplianceGuard (CCA) | Filing & court compliance | tests/test_cca_agent.py |
| AidConnector (LAF) | Legal aid correctness | tests/test_laf_agent.py |

---

## Workflow & Orchestration Validation

| Evaluation Goal | Test File |
|---------------|----------|
| Agent sequencing | tests/test_orchestrator_flow.py |
| Task routing | tests/test_orchestrator_flow.py |
| Session memory | tests/test_orchestrator_flow.py |
| Failure recovery | tests/test_orchestrator_flow.py |

---

## Retrieval & RAG Quality

**Metrics**
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)

**Tests**
- tests/test_vector_retrieval.py

Validated aspects:
- Chunk relevance
- Metadata alignment
- Semantic similarity accuracy

---

## Hallucination & Citation Safety (Critical)

| Safety Rule | Test File |
|-----------|----------|
| No fabricated cases | tests/test_citation_validator.py |
| Citation-source match | tests/test_citation_validator.py |
| Mandatory disclaimer | tests/test_citation_validator.py |

Any hallucination failure blocks deployment.

---

## API & Integration Validation

| Area | Test File |
|----|----------|
| Schema validation | tests/test_api_endpoints.py |
| Error handling | tests/test_api_endpoints.py |
| Rate limiting | tests/test_api_endpoints.py |

---

## Performance & Latency Benchmarks

**Target (Free Tier):**
- Average latency: < 5–7 seconds
- Graceful degradation under load

**Tests**
- evaluation/latency_benchmarks.py

---

## Human-in-the-Loop Enforcement
Mandatory review checkpoints:
- Final legal document drafts
- Novel legal interpretations
- Contradictory precedents

Automated tests verify presence of handoff flags before output finalization.

---

## Evaluation Artifacts

| Artifact | Location |
|-------|---------|
| Metrics & scores | outputs/evaluation_results/ |
| Hallucination logs | logs/agent_traces.log |
| Latency results | outputs/evaluation_results/latency.json |

---

## Continuous Improvement Loop
1. Run test suite
2. Capture failures
3. Patch agents/prompts
4. Re-run evaluations
5. Approve deployment

---

## Reviewer Assurance Statement
Every evaluation claim in Vidhi is backed by a named, executable test case.  
No unverifiable metrics. No hidden logic. Full audit readiness.
