## 1. Governance Objectives

Vidhi governance is built around these goals:

- Ensure outputs are **citation-backed and verifiable**
- Prevent the system from producing **legal advice**
- Prevent generation of **fabricated citations or fake case laws**
- Ensure **human verification is mandatory**
- Protect user privacy and sensitive legal documents
- Maintain responsible use aligned with the Indian legal ecosystem

---

## 2. Core Ethical Principles

### 2.1 Human-in-the-Loop First
All outputs must be treated as drafts and reviewed by a qualified legal professional.

### 2.2 Non-Deceptive Outputs
Vidhi must never pretend certainty when it is unsure.  
If the system cannot validate an answer with citations, it must respond with a limitation notice.

### 2.3 No Harmful Legal Enablement
Vidhi must refuse requests that:
- promote harassment, intimidation, or abuse
- help fabricate false evidence
- encourage illegal acts
- bypass court procedures unlawfully

### 2.4 Transparency and Traceability
Every generated output must include:
- retrieved sources (citations)
- confidence levels
- disclaimer and verification requirement

### 2.5 Data Privacy & Minimal Retention
User documents may contain:
- personal identifiers
- FIR details
- contracts
- medical or financial evidence

Vidhi must avoid storing such content permanently unless explicitly required.

---

## 3. Strict Policy Boundaries (What Vidhi Will NOT Do)

Vidhi must refuse or avoid the following:

### 3.1 No Legal Advice
Vidhi must not provide:
- final legal opinion
- "best strategy" as a definitive instruction
- guarantees of court outcomes

Allowed:
- summarization of precedents
- comparison of cases
- drafting support with citations

Not allowed:
- “You should file under Section X and you will win.”

### 3.2 No Fake Citations
Vidhi must never generate:
- invented SCC/AIR citations
- invented case titles
- invented court orders

If citations are missing, Vidhi must say:
> "Unable to locate verified citations. Please verify manually."

### 3.3 No Forgery or Fraud Support
Vidhi must refuse:
- drafting fake affidavits
- creating false evidence
- producing forged legal notices
- impersonation letters

### 3.4 No Sensitive/Personal Targeting
Vidhi must refuse:
- requests to doxx individuals
- harassment-based legal notices
- malicious defamation content

### 3.5 No Unauthorized Data Collection
Vidhi must not scrape:
- restricted websites
- private legal databases without permission
- copyrighted legal content where usage rights are unclear

---

## 4. Safety Guardrails in the System

Vidhi governance is enforced using technical controls:

### 4.1 SafetyGuardrails Module
The module ensures:
- unsafe prompts are rejected
- illegal instructions are blocked
- the system stays within educational + research scope

### 4.2 CitationValidator Module
Ensures:
- all cited cases exist in retrieved documents
- citation formatting is consistent
- citation confidence is tracked

### 4.3 Output Formatting Rules
Every output must include:
- disclaimer section
- citations section
- limitations section
- verification note

---

## 5. Mandatory Disclaimers

All generated documents must contain the following disclaimer:

> **Disclaimer:** Vidhi is a research and drafting assistant. It does not provide legal advice. All outputs must be reviewed and validated by a qualified lawyer before use in any court, tribunal, or legal proceeding.

---

## 6. Human Handoff Rules (Mandatory)

Vidhi must enforce human verification at key points:

### 6.1 Research Stage Handoff
Before drafting:
- user/lawyer must confirm retrieved precedents are relevant

### 6.2 Drafting Stage Handoff
Before final document export:
- lawyer must validate:
  - facts
  - arguments
  - sections
  - citations

### 6.3 Compliance Stage Handoff
Before filing:
- lawyer must verify court-specific requirements:
  - annexures
  - formatting
  - affidavits
  - fees

---

## 7. Acceptable Use Policy

### 7.1 Allowed Use
- legal research assistance
- summarization of judgments
- drafting petitions, notices, affidavits as drafts
- compliance checklists
- legal aid recommendations using verified sources

### 7.2 Prohibited Use
- generating false evidence
- threats or intimidation notices
- doxxing or harassment
- legal opinion without citations
- bypassing legal processes

---

## 8. Data Handling and Retention Policy

### 8.1 User Data
- user uploads should be stored locally by default
- avoid sending sensitive documents to external APIs unless required
- redact PII in logs

### 8.2 Logs
Logs should not store:
- full user documents
- Aadhaar/PAN numbers
- personal phone numbers or addresses

Store only:
- anonymized request metadata
- timestamps
- error messages

### 8.3 Retention Period (Recommended)
- raw user uploads: maximum 7 days (configurable)
- derived chunks/embeddings: maximum 30 days (configurable)
- audit logs: 30–90 days depending on environment

---

## 9. Model Governance Rules

### 9.1 Retrieval-First Answering
All answers must be based on retrieved documents.

### 9.2 Confidence Threshold
If retrieval confidence is low:
- output must be marked "LOW CONFIDENCE"
- system must recommend manual research

### 9.3 Model Versioning
Record:
- LLM version used
- embedding model used
- prompt version hash

---

## 10. Accountability and Ownership

| Governance Area | Responsibility |
|----------------|----------------|
| Safety rules enforcement | SafetyGuardrails |
| Citation integrity | CitationValidator |
| Compliance format rules | ComplianceGuard |
| Deployment security | DevOps/Security |
| Ethical policy updates | Governance Owner |

---

## 11. Governance Review Process

Governance policies must be reviewed:
- at every major release
- after any misuse incident
- after feedback from legal professionals

Suggested review cadence:
- monthly during development
- quarterly after stable release

---

## 12. Final Note

Vidhi is built with the philosophy:

> **"Assist legal research and drafting, but never replace legal judgment."**

This governance framework ensures the system remains safe, ethical, and aligned with real-world legal responsibility.
