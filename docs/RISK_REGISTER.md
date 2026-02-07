# Vidhi — Risk Register

This document lists the key risks identified for the **Vidhi** capstone project and recommended mitigations.  
Risks are categorized across technical, legal, ethical, operational, and project execution areas.

---

## Risk Scoring Model

- **Likelihood (L)**: 1 (Low) → 5 (High)  
- **Impact (I)**: 1 (Low) → 5 (High)  
- **Risk Score** = L × I

---

## Risk Register

| Risk ID | Risk Category | Risk Description | Likelihood (1-5) | Impact (1-5) | Score | Mitigation Strategy | Owner |
|--------|---------------|------------------|------------------|--------------|-------|---------------------|-------|
| R1 | Data | Court websites change HTML structure causing scrapers to fail | 4 | 3 | 12 | Use modular scrapers, versioned parsers, fallback to manual upload ingestion | Ingestion Lead |
| R2 | Data | Legal data sources may restrict scraping or automated extraction | 3 | 5 | 15 | Prefer official APIs/feeds if available, store only metadata, comply with robots.txt | Governance Owner |
| R3 | Legal | Copyright concerns on republishing judgments | 2 | 5 | 10 | Store references + citations; avoid redistributing full judgments unless legally permitted | Governance Owner |
| R4 | Retrieval | Wrong precedent retrieved due to weak embeddings or chunking | 4 | 4 | 16 | Hybrid retrieval, reranking, better chunking rules, evaluation dataset | Retrieval Lead |
| R5 | Hallucination | Model generates fake citations or fabricated case laws | 4 | 5 | 20 | Citation validator, enforce retrieval-only answers, "no-citation=no-answer" policy | Safety Lead |
| R6 | Hallucination | Incorrect section mapping (IPC/CrPC/CPC) | 3 | 4 | 12 | Add legal section lookup dictionary and verification checks | Agent Lead |
| R7 | Ethics | Users treat generated draft as legal advice and file without review | 4 | 5 | 20 | Mandatory disclaimers, human review checkpoints, UI warning banners | Product Owner |
| R8 | Security | Sensitive user documents stored insecurely | 3 | 5 | 15 | Local encryption, access controls, avoid storing PII by default | Security Owner |
| R9 | Security | API endpoints abused via high request volume (DoS) | 3 | 4 | 12 | Rate limiting middleware, request logging, throttling | API Lead |
| R10 | Operations | Free-tier deployment limitations (RAM, disk, uptime) | 4 | 3 | 12 | Lightweight services, caching, store large data in S3, restart scripts | DevOps Lead |
| R11 | Quality | Poor evaluation coverage leads to hidden failures | 3 | 4 | 12 | Automated evaluation pipeline, regression tests for agents | QA/Evaluation Lead |
| R12 | Governance | Bias or unfair suggestions in legal aid recommendations | 2 | 4 | 8 | Use verified legal aid directories only; avoid discriminatory language | Safety Lead |
| R13 | Compliance | Incorrect court filing format leads to rejection | 3 | 4 | 12 | ComplianceGuard rules, templates per court, lawyer verification step | Compliance Lead |
| R14 | Project | Scope creep (too many features, missed capstone deadline) | 4 | 4 | 16 | Roadmap prioritization, define MVP scope, weekly sprint review | Project Lead |
| R15 | Dependency | External API (LLM or embeddings) cost increase or downtime | 3 | 4 | 12 | Allow local embedding fallback; cache embeddings; retry strategies | Architecture Owner |
| R16 | Reliability | Vectorstore corruption or index mismatch | 2 | 4 | 8 | Index backups, checksum validation, rebuild pipeline | Retrieval Lead |
| R17 | Reputation | Misuse for unethical litigation or harassment | 2 | 5 | 10 | Strong policy rules; refusal patterns; governance logging | Governance Owner |

---

## High-Priority Risks (Top 5)

These require continuous monitoring:

1. **R5 Hallucinated citations (Score 20)**
2. **R7 Users treating output as legal advice (Score 20)**
3. **R4 Wrong precedent retrieval (Score 16)**
4. **R14 Scope creep / deadline risk (Score 16)**
5. **R2 Legal restrictions on scraping (Score 15)**

---

## Monitoring & Review Plan

- Review risks every sprint.
- Track incidents in GitHub issues with labels:
  - `risk`
  - `security`
  - `hallucination`
  - `compliance`
- Update mitigations as new risks are identified.

---

## Notes
This risk register is designed for an academic capstone project but follows industry-aligned risk practices for building systems in regulated domains like legal research.
