# Vidhi — Roadmap (Future Enhancements)

This document captures the planned evolution of **Vidhi** (Legal Case Research & Document Automation) beyond the current capstone scope. The roadmap focuses on making the platform more reliable, scalable, and usable for real-world Indian legal workflows while preserving ethical safeguards and human verification.

---

## 1. Short-Term Enhancements (0–3 Months)

### 1.1 Improve Retrieval Quality
- Add **query expansion** based on jurisdiction, case type, and legal sections.
- Add **hybrid retrieval** (keyword + vector search).
- Introduce **reranking models** to improve top-k result accuracy.
- Improve chunking rules for long judgments (headnotes vs reasoning vs final order).

### 1.2 Better Citation Verification
- Enforce structured citation format:
  - Court name
  - Case title
  - Citation ID (SCC / AIR / neutral citation if available)
  - Judgment date
- Add automatic citation cross-checking against known court sources.
- Add "Citation Confidence Score" for every output.

### 1.3 Enhanced Prompt Engineering
- Create agent-specific prompts for:
  - Bail
  - Writ petitions
  - Consumer disputes
  - Property disputes
- Add defensive prompting to prevent:
  - hallucinated citations
  - incorrect section references
  - fabricated party names

### 1.4 UI Improvements (Streamlit)
- Add guided intake form with dropdowns:
  - state
  - court
  - case category
- Add clickable citation viewer.
- Add document preview and download as PDF/Word.

---

## 2. Medium-Term Enhancements (3–6 Months)

### 2.1 Court-Specific Templates & Compliance Packs
- Add templates aligned to:
  - Supreme Court filing style
  - High Court writ format
  - District court plaint format
  - Tribunal petition format
- Build compliance rule packs for:
  - annexure naming
  - affidavit formatting
  - court fee reminders
  - limitation check reminders

### 2.2 Multi-Language Support
- Hindi + Marathi + Tamil + Telugu support for:
  - intake
  - summarization
  - drafting
- Use translation with legal glossary preservation.
- Add language detection during ingestion.

### 2.3 Stronger Human-in-the-Loop Workflow
- Add review checkpoints:
  - research report approval
  - argument approval
  - draft approval
- Add “Reviewer Notes” section in generated documents.
- Add version tracking for drafts.

### 2.4 Feedback Learning Loop
- Capture feedback from lawyer review:
  - correct/incorrect citations
  - missing cases
  - wrong legal sections
- Use feedback to improve retrieval ranking and prompts.

---

## 3. Long-Term Enhancements (6–12 Months)

### 3.1 Enterprise-Grade Deployment
- Move from single-machine deployment to:
  - containerized microservices
  - separate ingestion service
  - separate retrieval service
- Add load balancing and autoscaling (AWS ECS / EKS).

### 3.2 Observability & Monitoring
- Add full monitoring stack:
  - API latency
  - error rates
  - retrieval hit-rate
  - hallucination detection rate
- Add dashboard for agent performance and failure analysis.

### 3.3 Secure User Workspace & Document Vault
- Add authentication and user profiles.
- Secure storage for user documents and drafts.
- Provide per-user workspace isolation.

### 3.4 Advanced Legal Intelligence
- Add argument outcome prediction (experimental).
- Add judge/bench tendency analysis (high-risk ethically; must be controlled).
- Add similarity search for factual patterns across cases.

---

## 4. AI/Agent Improvements

### 4.1 Agent Specialization Packs
Introduce specialized agents for:
- **Evidence Analyzer Agent** (extract key evidence from FIR/complaints/contracts)
- **Contract Clause Finder Agent**
- **Judgment Summarizer Agent**
- **Precedent Contradiction Detector Agent**

### 4.2 Better Planning and Orchestration
- Add multi-step planning:
  - research plan → execute → validate → draft
- Add fallback strategies:
  - if retrieval fails → ask user clarifying questions
  - if citations missing → return partial answer with warnings

---

## 5. Dataset & Knowledge Expansion

### 5.1 Expand Legal Data Sources
- Add official state High Court websites systematically.
- Add tribunal portals:
  - NCLT
  - NCLAT
  - CAT
  - ITAT
  - Consumer Forums
- Add bare acts, amendments, and official gazette notifications.

### 5.2 Metadata Enrichment
Extract and store:
- judge names
- bench strength
- final disposition (allowed/dismissed/partly allowed)
- acts/sections referenced
- case category tags

---

## 6. Compliance & Governance Enhancements

### 6.1 Stronger Safety Guardrails
- Automatically refuse outputs that:
  - encourage illegal acts
  - provide legal advice as final opinion
  - fabricate citations
- Add forced disclaimers in every draft.

### 6.2 Audit-Ready Logging
- Maintain full traceability:
  - prompt version
  - retrieved sources
  - agent outputs
  - final document version

---

## 7. Product & Adoption Roadmap

### 7.1 Community / Open Source Adoption
- Add contribution labels and good-first-issues.
- Provide demo datasets and sample workflows.
- Add Docker-based quick start.

### 7.2 Professional Edition (Optional Future)
Possible add-ons:
- Court filing workflow assistant
- Document vault with encryption
- Role-based access control
- Multi-user collaboration

---

## 8. Roadmap Summary Table

| Timeline | Focus Area | Planned Outcomes |
|---------|------------|------------------|
| 0–3 months | Retrieval + citation validation | Higher research accuracy and reduced hallucinations |
| 3–6 months | Templates + multilingual + review workflow | Better usability for real legal workflows |
| 6–12 months | Enterprise deployment + monitoring | Scalable and reliable platform |
| 12+ months | Advanced legal intelligence | Experimental features with strong governance |

---

## Notes
This roadmap is intentionally designed to ensure Vidhi remains:
- **human-verified**
- **citation-backed**
- **ethically controlled**
- **safe for educational and professional environments**
