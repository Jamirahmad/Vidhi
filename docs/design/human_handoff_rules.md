# Human Handoff Rules (Human-in-the-Loop Workflow)

## Overview

Vidhi is designed as an **assistive legal research and drafting system** for the Indian legal ecosystem.  
It **does not provide legal advice** and must always operate under **human verification**.

This document defines:

- When Vidhi must hand off outputs to a human
- What the human reviewer must validate
- What Vidhi is allowed vs not allowed to do
- Risk-based escalation rules
- Mandatory approval checkpoints for document drafting and citations

---

## Why Human Handoff is Mandatory

Legal workflows are highly sensitive because:

- Wrong citations can mislead courts or clients.
- Incorrect limitation analysis can cause case dismissal.
- Wrong legal sections can invalidate petitions.
- Fabricated or hallucinated precedents can create professional misconduct risk.
- Court formatting and procedural compliance differs by jurisdiction.

Therefore, Vidhi is built on the principle:

> **"Automation assists speed, but human judgment owns responsibility."**

---

## Human Handoff Points in the Workflow

Vidhi operates as a multi-agent pipeline. Human handoff is required at key checkpoints.

### Workflow Stages

1. Case Intake  
2. Research & Retrieval  
3. Issue Identification  
4. Limitation Analysis  
5. Argument Construction  
6. Draft Document Generation  
7. Compliance & Filing Validation  
8. Final Packaging  
9. Human Lawyer Review (Mandatory)

---

## Mandatory Human Review Checkpoints

### Handoff Rule #1 — Case Facts Confirmation (Mandatory)

**Trigger:** User submits case facts.

**Reason:** Incorrect facts lead to wrong retrieval and wrong drafting.

**Human must verify:**
- Parties and roles are correct (petitioner/respondent)
- Dates are accurate
- Jurisdiction is correct (State, Court)
- Case type is correct (Civil/Criminal/Tribunal)

**Vidhi Output:**
- A structured summary of facts
- Clarifying questions if missing information is detected

**Handoff Required:** Yes

---

### Handoff Rule #2 — Citation Validation (Mandatory)

**Trigger:** CaseFinder returns precedents.

**Reason:** Hallucinated citations are a major legal risk.

**Human must verify:**
- Citation exists in official database
- Citation text matches actual judgment
- Court and bench details are correct
- Date and case number match

**Vidhi Output:**
- List of citations
- Source links (where available)
- Metadata (court, year, bench, petition type)

**Handoff Required:** Yes  
**Agent Responsible:** CaseFinder + CitationValidator

---

### Handoff Rule #3 — Contradictory Precedents Flag (Mandatory)

**Trigger:** ArgumentBuilder identifies conflicting case laws.

**Reason:** Lawyers must decide which precedents are stronger and how to position them.

**Human must verify:**
- Which precedents apply to the jurisdiction
- Whether case laws are overruled or distinguished
- Whether newer judgments exist

**Vidhi Output:**
- Contradiction map (supporting vs opposing cases)
- Suggested reasoning, not final legal conclusion

**Handoff Required:** Yes

---

### Handoff Rule #4 — Limitation Period Final Decision (Mandatory)

**Trigger:** LimitationChecker produces time-bar analysis.

**Reason:** Limitation errors can cause rejection/dismissal.

**Human must verify:**
- Start date of limitation is correct
- Whether condonation applies
- Whether exceptions apply (fraud, discovery rule, continuous cause, etc.)
- Whether specific tribunal/court rules override general rules

**Vidhi Output:**
- Limitation calculation explanation
- Confidence score
- Applicable act references (Limitation Act, special acts)

**Handoff Required:** Yes  
**Agent Responsible:** LimitationChecker

---

### Handoff Rule #5 — Draft Document Approval Before Use (Mandatory)

**Trigger:** DocComposer generates draft petition/notice/affidavit.

**Reason:** Generated documents may contain missing annexures, wrong language, or procedural gaps.

**Human must verify:**
- Correct sections and prayer clauses
- Correct party details
- Correct court format and jurisdiction
- Correct annexures list
- No false claims or unsupported statements

**Vidhi Output:**
- Draft document (structured markdown or doc format)
- Citation-backed paragraphs
- Annexure checklist

**Handoff Required:** Yes  
**Agent Responsible:** DocComposer

---

### Handoff Rule #6 — Compliance Report Review (Mandatory)

**Trigger:** ComplianceGuard completes compliance validation.

**Reason:** Filing rules vary widely.

**Human must verify:**
- Court-specific formatting requirements
- Fee calculation accuracy
- Required affidavits and annexures
- Proper indexing and pagination
- Notarization requirements
- Vakalatnama requirements

**Vidhi Output:**
- Compliance checklist
- Missing elements list
- Filing-ready packaging guidance

**Handoff Required:** Yes  
**Agent Responsible:** ComplianceGuard

---

### Handoff Rule #7 — Legal Aid Suggestions Verification (Optional but Recommended)

**Trigger:** AidConnector recommends legal aid.

**Reason:** Legal aid eligibility differs based on state, income, and case type.

**Human must verify:**
- Eligibility criteria match user profile
- Suggested contacts are active and official

**Vidhi Output:**
- Legal aid options (NALSA, state legal services authority, NGO contacts)
- Reference links

**Handoff Required:** Optional (Recommended)

---

## High-Risk Escalation Rules

Some scenarios are automatically classified as **high-risk**, requiring stronger human intervention.

### High-Risk Categories

| Category | Examples |
|---------|----------|
| Criminal matters | Bail, murder, rape, terrorism, narcotics |
| Juvenile cases | POCSO, minor involvement |
| Constitutional matters | writ petitions, PIL |
| High-value civil disputes | large financial fraud, property disputes |
| Family law | divorce, custody |
| Corporate insolvency | NCLT / IBC matters |
| National security / sensitive topics | sedition, UAPA |
| Medical negligence | high consequence litigation |

---

### High-Risk Escalation Policy

If a case falls into a high-risk category:

- Vidhi must display a warning banner
- Drafting must be marked as **"Not Filing Ready"**
- Confidence scoring must be included
- Citations must include source links wherever possible
- Human review is mandatory before any output is used externally

---

## Confidence-Based Handoff Rules

Vidhi assigns confidence scores based on retrieval quality, citation validation, and model response reliability.

### Confidence Levels

| Confidence | Meaning | Action |
|----------|---------|--------|
| High (80–100%) | Strong citations, consistent retrieval | Human review required (standard) |
| Medium (50–79%) | Partial coverage, possible missing cases | Human review required + recommend manual research |
| Low (0–49%) | Weak retrieval, missing citations | Mandatory escalation + system should not draft final document |

---

### Low Confidence Automatic Restrictions

If confidence is low, Vidhi must:

- Avoid definitive legal statements
- Avoid producing a full petition draft
- Only produce a research summary + questions
- Request user to upload documents for clarification

---

## Hallucination Prevention Handoff Rules

### Rule: "No Citation, No Claim"

Vidhi must follow:

> If a legal claim references a precedent, it must be backed by a valid citation.

If a citation cannot be validated, the output must explicitly say:

- "Citation requires verification"
- "Not confirmed from official source"

---

### Rule: "No Fabricated Case Names"

If the system generates a case name without an official citation:

- It must be removed or flagged.
- It must never be presented as factual.

---

## Output Packaging Rules

All final outputs must be delivered with:

### Research Report Output Must Include

- List of retrieved judgments
- Court, year, and citation format
- Short case summary
- Key ratio decidendi (if extractable)
- Relevance scoring
- Contradictions / overruling warnings

### Draft Document Output Must Include

- Document type (Bail Application / Legal Notice / Affidavit etc.)
- Jurisdiction format
- Annexure checklist
- Citations used in each section
- "Human verification required" disclaimer

---

## Legal Disclaimer Display Requirements

Vidhi must always show this disclaimer prominently:

> Vidhi is a research and drafting assistant.  
> It does not provide legal advice.  
> All outputs must be reviewed and validated by a qualified lawyer before use.

This disclaimer must appear in:

- UI (Streamlit)
- API response metadata
- Exported research reports
- Exported draft documents

---

## Human Reviewer Responsibilities

### Lawyer / Human Reviewer Must Validate

- Correctness of legal interpretation
- Case applicability in the jurisdiction
- Updated status (overruled / distinguished / pending)
- Correct legal sections
- Correct limitation and procedural compliance
- Ethical appropriateness of the drafted content

---

## What Vidhi Must Never Do (Hard Rules)

Vidhi must not:

- Guarantee outcomes (e.g., "You will get bail")
- Provide final legal advice
- Recommend illegal actions
- Fabricate judgments or citations
- Misrepresent legal precedents
- Draft documents without disclaimers
- Encourage filing without lawyer review

---

## Human Override Rules

Humans can override Vidhi suggestions only if:

- They confirm sources independently
- They update citations with verified references
- They adjust drafting to match court requirements

Vidhi must log all overrides as feedback for evaluation.

---

## Audit Logging and Traceability Requirements

For governance and debugging, Vidhi must store:

- Timestamp of workflow execution
- User input summary (excluding sensitive data if configured)
- Agent outputs
- Citations used
- Confidence scores
- Human override feedback

This ensures:

- Traceability for debugging
- Compliance for governance review
- Continuous improvement for evaluation

---

## Recommended Human Handoff UI Design (Best Practice)

The UI should provide:

- "Review Required" status label
- "Verified" checkbox for citations
- "Approve Draft" button
- "Send for Lawyer Review" export option
- "Risk Warning" banner for high-risk categories

---

## Summary: Human Handoff Rule Checklist

| Stage | Mandatory Human Review? | Why |
|------|--------------------------|-----|
| Case Facts | Yes | Wrong facts = wrong research |
| Case Retrieval | Yes | Avoid hallucinated precedents |
| Issue Identification | Recommended | Ensure correct sections |
| Limitation Analysis | Yes | Time-bar risk |
| Argument Builder | Yes | Contradiction handling |
| Draft Document | Yes | Filing correctness |
| Compliance Check | Yes | Court-specific rules |
| Legal Aid Suggestions | Optional | Eligibility varies |

---

## Final Policy Statement

Vidhi is not an autonomous legal decision-maker.  
It is a structured assistant designed for speed and organization.

**Every research report and document draft must pass through human review before real-world usage.**
