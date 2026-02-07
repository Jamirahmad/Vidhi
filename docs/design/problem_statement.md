# Problem Statement

## Background

India has one of the largest and most complex legal ecosystems in the world, spanning multiple levels of courts and tribunals such as:

- Supreme Court of India
- High Courts across states
- District courts
- Tribunals (NCLT, NCDRC, CAT, ITAT, etc.)

Despite ongoing digitization efforts, legal research and drafting remain highly manual and time-consuming.

Legal professionals, especially junior advocates and litigants, often spend a significant amount of time locating relevant case laws, identifying applicable statutes, and drafting documents using repetitive templates.

---

## The Core Problem

Legal case research and drafting in India is slow, fragmented, and highly dependent on manual effort.

A typical legal workflow involves:

- collecting case facts and supporting documents
- identifying applicable laws and sections
- searching for relevant precedents
- validating citations and ensuring authenticity
- preparing arguments and counter-arguments
- drafting petitions/notices/affidavits
- ensuring court-specific compliance and formatting

This process is often repeated for each new matter, even when similar precedents and document structures already exist.

---

## Key Challenges in the Indian Legal System

### 1. Massive Case Backlog and Delays

India’s judiciary has a backlog of **crores of pending cases**, resulting in significant delays.  
Lawyers and litigants face pressure to prepare documents quickly and respond within strict timelines.

However, manual legal research can take **days to weeks**, delaying filings and case progression.

---

### 2. Research Effort is High and Repetitive

Lawyers spend substantial time on tasks such as:

- searching similar judgments
- extracting ratio decidendi
- mapping relevant sections of law
- identifying contradictory precedents
- summarizing judgments for case strategy

This research is often repetitive and depends heavily on the individual’s experience.

---

### 3. Fragmented Legal Data Sources

Legal information in India is distributed across multiple platforms:

- official court portals (SC/HC websites)
- tribunal portals
- gazette notifications
- government legal portals
- paid legal databases (SCC Online, Manupatra, etc.)

The availability of judgments varies widely, and many sources lack consistent APIs or structured metadata.

---

### 4. Citation and Authenticity Validation is Hard

A critical legal risk is the use of:

- incorrect citations
- incomplete judgments
- outdated precedents
- judgments without official metadata

Validating whether a citation is real and applicable is time-consuming, but necessary to avoid legal and professional consequences.

---

### 5. Drafting is Template-Driven but Error-Prone

Drafting legal documents often relies on:

- older templates
- previous case files
- copied clauses
- informal office formats

This creates risk of:

- missing annexures
- wrong party details
- incorrect prayer clauses
- incorrect jurisdiction formatting
- outdated legal references

Even minor drafting errors can lead to court objections or delays.

---

### 6. Procedural Compliance Varies by Court

Court requirements differ based on:

- jurisdiction (state/court)
- case type (civil/criminal/tribunal)
- filing procedures
- annexure structure
- affidavit requirements
- formatting rules
- fees and stamps

A single missed requirement can result in rejection or filing delays.

---

### 7. Access Gap for Litigants and Small Law Firms

Many litigants and small law firms struggle due to:

- limited access to paid databases
- lack of trained junior associates
- limited time for research
- lack of standardized drafting support

This creates an uneven playing field where only large firms can consistently scale legal research.

---

## Current State (As-Is Scenario)

### Typical Workflow Today

1. Client shares facts and documents  
2. Lawyer manually reads and interprets facts  
3. Junior associates search case laws manually  
4. Citations are copied from sources and validated manually  
5. Arguments are prepared using prior experience  
6. Draft is created using old templates  
7. Court compliance is checked manually  
8. Final filing is prepared

### Time and Effort Cost

- Legal research may take **10–60 hours**
- Drafting may take **4–12 hours**
- Compliance checks add additional time
- Rework is common due to missing information

---

## Impact of the Problem

### Impact on Legal Professionals

- reduced productivity
- high dependency on junior staff
- increased drafting errors
- inconsistent research quality
- delayed filings and responses

### Impact on Litigants

- higher legal costs
- delayed justice
- reduced access to legal help
- difficulty understanding legal procedures

### Impact on the Judicial System

- increased filing errors
- procedural delays
- higher burden on court staff
- inconsistent quality of submissions

---

## Proposed Opportunity

There is a strong need for a system that can:

- assist with structured legal research
- retrieve precedents with verifiable citations
- summarize relevant judgments
- draft legal documents aligned to jurisdiction
- check compliance requirements
- enforce ethical and safety boundaries
- keep humans (lawyers) in the loop

---

## Problem Statement (Formal Definition)

> **Design and build an assistive system for the Indian legal ecosystem that can reduce the manual effort required for legal research and drafting by using structured retrieval, citation validation, and multi-agent workflows, while enforcing ethical boundaries and requiring human verification for all outputs.**

---

## What the Solution Must Achieve

The solution should be able to:

- accept case facts, issues, jurisdiction, and case type
- retrieve relevant case laws and statutory references
- identify key issues and applicable legal sections
- generate structured arguments and counter-arguments
- draft petitions/notices/affidavits with citations
- validate formatting and compliance requirements
- produce outputs suitable for lawyer review
- avoid hallucinations and fabricated citations
- enforce mandatory human handoff

---

## Key Success Criteria

A successful solution should demonstrate:

- improved speed of legal research
- structured and traceable citations
- reduced drafting errors
- improved consistency across documents
- strong human-in-the-loop workflow
- measurable evaluation metrics (citation accuracy, retrieval relevance, hallucination rate)

---

## Final Note

Vidhi is intended to be an **assistive legal workflow accelerator**, not an autonomous legal decision-maker.  
It aims to reduce the manual burden on lawyers and litigants while ensuring responsible usage through strict verification and governance rules.
