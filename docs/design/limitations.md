# Limitations (Non-Goals and Known Constraints)

## Overview

Vidhi is a **legal research and document drafting assistant** for the Indian legal ecosystem.  
It is designed to accelerate research, structure arguments, and draft documents with citations — but it is **not a replacement for a lawyer**.

This document clearly defines Vidhi’s limitations, boundaries, and non-goals to ensure safe and ethical usage.

---

## Core Limitations

### 1. Vidhi Does Not Provide Legal Advice

Vidhi can summarize laws, retrieve precedents, and draft documents, but it **cannot provide final legal advice** such as:

- “You should file a writ petition.”
- “This case will definitely succeed.”
- “You will get bail.”

Any decision-making must be performed by a **qualified legal professional**.

---

### 2. Outputs Are Not Filing-Ready Without Human Review

Even if Vidhi generates a complete petition or legal notice, it must be treated as:

> **Draft content only**

Court filing requires human verification of:

- accuracy of facts
- correctness of citations
- compliance with jurisdiction rules
- formatting and annexures
- appropriate legal positioning

---

### 3. Citations May Be Incomplete or Unverified

Vidhi’s retrieval process may return:

- partial judgments
- incomplete PDF scans
- missing bench details
- judgments without authoritative citation formatting
- documents with OCR errors

If official court databases are unavailable or blocked, Vidhi may not confirm authenticity of a citation.

**All citations must be validated by humans before use.**

---

### 4. Data Availability Constraints (Indian Legal Sources)

Indian legal datasets are fragmented across:

- Supreme Court portal
- High Court websites
- tribunal portals
- gazette notifications
- commercial databases (restricted)

Many sources may have:

- CAPTCHA
- anti-scraping restrictions
- inconsistent HTML formats
- non-standard PDF scans
- missing metadata

As a result, Vidhi may not always retrieve the best or latest judgment.

---

### 5. No Guarantee of Latest Legal Updates

Vidhi may not reflect the latest:

- amendments to acts
- newly passed bills
- repealed sections
- new Supreme Court interpretations
- updated procedural rules

This is especially critical in fast-changing domains like:

- taxation
- GST
- IT Act
- corporate law
- insolvency law
- cybercrime regulations

Human verification is mandatory.

---

### 6. Overruling / Distinguishing Detection May Be Inaccurate

Vidhi may not reliably detect whether a case has been:

- overruled
- distinguished
- reversed
- stayed
- partially modified

Unless the judgment text explicitly mentions it or the metadata is available, Vidhi might incorrectly treat an outdated precedent as valid.

---

### 7. Jurisdiction-Specific Practices May Not Be Fully Captured

Indian courts have different procedural expectations:

- formats differ across High Courts
- tribunal filing rules vary
- district court practices differ state-to-state
- affidavit templates vary
- language requirements vary

Vidhi can provide **general drafting support**, but may not match the exact court clerk expectations without customization.

---

### 8. Document Drafting Quality Depends on Input Quality

If users provide incomplete case facts, Vidhi may produce:

- vague drafts
- incorrect assumptions
- missing annexures
- wrong prayer clauses
- wrong party roles

Vidhi cannot compensate for missing facts without user clarification.

---

### 9. Complex Litigation Strategy is Out of Scope

Vidhi does not replace professional litigation strategy such as:

- deciding whether to settle or fight
- advising on cross-examination strategy
- selecting best forum for filing
- deciding whether to invoke constitutional remedies
- advising whether to appeal or review

Vidhi may suggest **structured options**, but not final legal strategy.

---

### 10. Limited Support for Unstructured Evidence Files

Vidhi may struggle with:

- handwritten documents
- scanned affidavits
- regional language scans
- low-quality images
- unclear PDFs

OCR extraction may fail or introduce errors, leading to incomplete research or wrong document drafts.

---

## AI / Model Limitations

### 11. Hallucination Risk Exists (Even with Guardrails)

Even with retrieval-based grounding, LLMs can:

- misquote judgments
- incorrectly interpret ratio decidendi
- merge multiple cases into one explanation
- generate plausible but false legal reasoning

Vidhi mitigates this through:

- citation validation checks
- structured output formatting
- confidence scoring
- mandatory human review

But hallucination risk cannot be eliminated fully.

---

### 12. Lack of True Legal Reasoning

Vidhi can generate legal-sounding reasoning, but it does not have:

- courtroom experience
- context awareness like a lawyer
- ability to judge evidentiary strength
- deep legal intuition

It operates as a structured assistant, not a legal practitioner.

---

### 13. Multilingual Output Limitations

Vidhi may support translation, but:

- legal Hindi/Marathi/Tamil drafting has specialized vocabulary
- translations may not preserve exact legal meaning
- court drafting language is often rigid

Hence, multilingual drafting should be treated as **assistance**, not final output.

---

## System and Deployment Limitations

### 14. Free-Tier Deployment Constraints

When deployed using free-tier infrastructure (AWS Free Tier / Streamlit Cloud / Render):

- limited storage
- limited CPU/RAM
- slower indexing and retrieval
- smaller vector databases
- limited concurrency

Large-scale ingestion of Supreme Court + all High Courts may not be feasible under free-tier limits.

---

### 15. Vector Store Scaling Constraints

FAISS/Chroma performance depends on:

- embedding size
- number of documents
- chunking strategy
- index rebuild frequency

As dataset grows, retrieval speed may degrade unless infrastructure is upgraded.

---

### 16. Data Freshness is Not Continuous by Default

Unless scheduled ingestion pipelines are enabled, Vidhi will not automatically refresh:

- new judgments daily
- newly uploaded tribunal orders
- new circulars and gazette updates

Data freshness requires a pipeline + compute budget.

---

## Compliance & Governance Limitations

### 17. No Guarantee of Professional Compliance

Vidhi can assist with compliance checklists, but it cannot guarantee:

- court acceptance
- clerk approval
- correct stamping and fees
- notarization correctness

Final compliance must be validated by lawyers and clerks.

---

### 18. Not a Substitute for Bar Council Standards

Vidhi cannot ensure adherence to:

- advocate professional conduct rules
- client confidentiality obligations
- local bar practices

Users must follow applicable professional codes and legal standards.

---

## Ethical and Safety Constraints (Hard Boundaries)

### 19. No Assistance for Illegal or Harmful Requests

Vidhi must refuse or restrict:

- forged documents
- fraudulent evidence creation
- harassment notices
- blackmail-style legal threats
- manipulation of judicial outcomes
- false affidavits

---

### 20. Sensitive Criminal Matters Require Strong Escalation

For high-risk domains (e.g., terrorism, POCSO, narcotics):

- Vidhi must display warnings
- require mandatory lawyer involvement
- restrict overconfident drafting

---

## Non-Goals (Explicit Out-of-Scope Areas)

Vidhi is NOT designed to:

- represent users in court
- provide litigation guarantees
- file cases automatically
- generate final signed affidavits
- replace case management systems
- perform judge outcome prediction
- act as a legal consultant

---

## Known Data Gaps in Indian Legal Ecosystem

Vidhi may have incomplete coverage for:

- district court judgments (many not digitized)
- old pre-2000 judgments not digitized
- tribunal orders published inconsistently
- local gazette notifications not indexed properly
- paid legal database content (SCC Online, Manupatra, etc.)

---

## Summary

Vidhi is best positioned as:

✅ A research accelerator  
✅ A structured drafting assistant  
✅ A citation-driven discovery tool  
✅ A compliance checklist generator  
✅ A human-assisted legal workflow enabler  

Vidhi is NOT:

❌ a legal advisor  
❌ a court-ready petition filing system  
❌ a substitute for lawyer expertise  
❌ a guarantee of correct legal interpretation  

---

## Final Disclaimer

Vidhi is an educational and research project.  
All outputs must be reviewed and validated by a qualified legal professional before being used for filing, submission, or client communication.
