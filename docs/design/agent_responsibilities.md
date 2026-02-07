# Agent Responsibilities — Vidhi

This document defines the **responsibilities, inputs, outputs, and boundaries** of each agent in the Vidhi multi-agent system.

Vidhi is designed as an **assistive legal research and drafting platform** for the Indian legal ecosystem.  
All outputs must be **human-verified** before being used in real legal proceedings.

---

## Overview of Multi-Agent System

Vidhi follows a structured multi-agent workflow:

1. **LegalOrchestrator** manages the workflow
2. **CaseFinder** retrieves relevant case laws and statutes
3. **IssueSpotter** identifies legal issues and applicable sections
4. **LimitationChecker** checks limitation and time-bar applicability
5. **ArgumentBuilder** generates structured legal arguments
6. **DocComposer** drafts legal documents
7. **ComplianceGuard** validates filing compliance and formatting
8. **AidConnector** suggests legal aid / pro-bono resources

Each agent has a **single clear responsibility** and communicates through the Orchestrator.

---

# Agent Responsibilities

---

## 1. LegalOrchestrator (LRA)

### Purpose
The LegalOrchestrator is the **central workflow manager** of Vidhi.  
It coordinates all agents, maintains state, enforces safety rules, and ensures outputs are packaged correctly.

### Responsibilities
- Accept user case input (facts, jurisdiction, case type)
- Decide which agents must run and in what order
- Route tasks to the correct agent
- Maintain session memory and conversation history
- Enforce safety boundaries and ethical guardrails
- Track progress, errors, retries, and fallbacks
- Assemble final outputs into a unified response package

### Inputs
- Case facts
- Jurisdiction (State / Court)
- Case type (civil/criminal/tribunal)
- Optional: uploaded documents (PDF/DOCX)
- Optional: user preferences (language, document format)

### Outputs
- Structured workflow execution plan
- Agent task routing decisions
- Final response package including:
  - Research report
  - Draft document
  - Compliance checklist
  - Legal aid suggestions (if applicable)

### Boundaries / Rules
- Must not generate legal advice itself
- Must not bypass human verification requirements
- Must reject unsafe or unethical requests

---

## 2. CaseFinder (CLSA)

### Purpose
CaseFinder is responsible for **finding relevant case laws, precedents, and statutory references**.

### Responsibilities
- Convert case facts into search queries
- Retrieve relevant Supreme Court / High Court / tribunal judgments
- Retrieve statutory provisions (IPC, CrPC, CPC, Evidence Act, etc.)
- Rank results based on relevance
- Extract citations and court metadata
- Identify conflicting precedents (supporting vs opposing)

### Inputs
- Case summary from Orchestrator
- Jurisdiction filters (state/court)
- Case type and subject domain (criminal/civil/consumer/labour)

### Outputs
- Ranked list of relevant precedents with:
  - Title
  - Court name
  - Date
  - Citation
  - URL (if available)
  - Extracted reasoning snippet
- Statute / section references

### Boundaries / Rules
- Must not hallucinate citations
- Must not cite unverifiable sources
- Must include source references wherever possible

---

## 3. IssueSpotter (LII)

### Purpose
IssueSpotter identifies the **legal issues, legal provisions, and fact patterns** relevant to the case.

### Responsibilities
- Extract key facts from user input
- Identify legal issues and sub-issues
- Identify applicable statutes and sections (IPC, CrPC, CPC, Constitution, etc.)
- Detect missing facts needed for stronger legal reasoning
- Create structured case issue summary

### Inputs
- User facts
- Precedent list from CaseFinder

### Outputs
- Issue Report containing:
  - Primary legal issue(s)
  - Secondary issues
  - Applicable acts/sections
  - Required evidence checklist
  - Missing fact questions for the user

### Boundaries / Rules
- Must not provide legal opinions
- Must only classify and structure issues based on provided facts

---

## 4. LimitationChecker (LAA)

### Purpose
LimitationChecker evaluates whether the case is **time-barred**, and checks limitation-related warnings.

### Responsibilities
- Determine limitation period based on case type and legal provisions
- Check if filing is time-barred or within time
- Identify exceptions or condonation possibilities
- Flag missing date details that are required for accurate assessment
- Provide limitation risk warnings

### Inputs
- Key dates from user (incident date, filing date, notice date, etc.)
- Case type and jurisdiction
- Relevant sections identified by IssueSpotter

### Outputs
- Limitation Analysis Report including:
  - Applicable limitation period
  - Limitation expiry estimate
  - Whether delay condonation may apply
  - Risk score (Low/Medium/High)

### Boundaries / Rules
- Must explicitly mention if date data is insufficient
- Must not guarantee limitation outcomes
- Must request human review for edge cases

---

## 5. ArgumentBuilder (LAB)

### Purpose
ArgumentBuilder creates a structured argument framework based on facts, issues, and precedents.

### Responsibilities
- Build arguments supporting the user’s position
- Build counter-arguments (opposition side view)
- Connect each argument to precedents or statutory provisions
- Generate a logical argument tree:
  - claim → reasoning → precedent support → relief sought
- Identify weak points in the case

### Inputs
- Issue Report from IssueSpotter
- Case laws from CaseFinder
- Limitation analysis from LimitationChecker

### Outputs
- Argument Pack containing:
  - Supporting arguments
  - Counter arguments
  - Suggested responses to counter arguments
  - Citation links to precedents
  - Risk areas

### Boundaries / Rules
- Must not invent case laws
- Must label uncertain reasoning clearly
- Must always provide supporting sources

---

## 6. DocComposer (DGA)

### Purpose
DocComposer generates structured **legal draft documents** based on templates.

### Responsibilities
- Draft legal documents such as:
  - bail application
  - legal notice
  - civil suit plaint
  - affidavit
  - writ petition
- Ensure document follows template structure
- Use citations and sections referenced earlier
- Maintain neutral legal drafting tone
- Generate annexure references (if applicable)

### Inputs
- Argument Pack
- Issue Report
- User case details
- Document type request (notice/petition/bail/etc.)
- Templates stored in `src/prompts/templates/`

### Outputs
- Draft legal document in:
  - Markdown format
  - Optional export-ready formats later (PDF/DOCX)

### Boundaries / Rules
- Must not provide legal advice, only drafting assistance
- Must insert placeholders where facts are missing
- Must clearly mark sections requiring human lawyer input

---

## 7. ComplianceGuard (CCA)

### Purpose
ComplianceGuard checks whether the drafted document meets **court filing requirements and formatting rules**.

### Responsibilities
- Validate document formatting:
  - headings, numbering, annexures
- Check mandatory components:
  - parties, jurisdiction clause, cause of action, relief, verification
- Identify missing annexures or affidavits
- Flag inconsistent citations or missing references
- Suggest corrections to meet court-specific compliance

### Inputs
- Draft document from DocComposer
- Jurisdiction and court type
- Filing rules dataset (future enhancement)

### Outputs
- Compliance Report containing:
  - checklist of required elements
  - missing sections
  - formatting improvements
  - risk warnings
  - recommended attachments

### Boundaries / Rules
- Must not claim filing is "fully compliant"
- Must clearly mention that court rules vary
- Must recommend lawyer review before filing

---

## 8. AidConnector (LAF)

### Purpose
AidConnector provides suggestions for **legal aid, pro-bono, and public resources** for users.

### Responsibilities
- Identify legal aid eligibility hints based on case type
- Suggest resources such as:
  - NALSA / SALSA
  - district legal services authority
  - legal aid clinics
  - NGO support for women/children/labour
- Provide general guidance on where to seek help

### Inputs
- Jurisdiction (state/district)
- Case type
- User preference (optional)

### Outputs
- Legal Aid Report containing:
  - suggested resources
  - relevant government portals
  - contact / office guidance (if publicly available)

### Boundaries / Rules
- Must not guarantee eligibility
- Must not provide sensitive personal legal advice
- Must cite only official resources

---

# Agent Interaction Rules

## Standard Workflow Sequence

1. Orchestrator validates input + loads session
2. CaseFinder retrieves relevant precedents
3. IssueSpotter extracts issues + legal provisions
4. LimitationChecker flags limitation/time-bar concerns
5. ArgumentBuilder builds arguments + counter-arguments
6. DocComposer drafts the legal document
7. ComplianceGuard validates filing readiness
8. AidConnector suggests legal aid (optional)
9. Orchestrator packages output + enforces human review

---

# Human Handoff Rules (Mandatory)

Vidhi enforces **Human-in-the-Loop (HITL)** verification.

Human handoff is required when:

- citations cannot be verified
- limitation is unclear or based on incomplete dates
- conflicting precedents are found
- document impacts liberty (bail, criminal cases)
- sensitive categories appear (juvenile, sexual offences, domestic violence)
- constitutional or PIL matters arise
- the user requests direct legal advice

---

# Output Format Standard (All Agents)

Each agent must return output in a structured format:

- `summary`
- `details`
- `citations`
- `assumptions`
- `missing_inputs`
- `confidence_score`

This ensures outputs are consistent and traceable.

---

# Safety Boundaries (Non-Negotiable)

Vidhi must not:

- fabricate citations or case law references
- provide definitive legal advice or court outcome predictions
- encourage illegal activity or fraud
- create forged legal documents
- generate misleading filings without disclaimers

---

# Future Enhancements

- court-specific compliance rules database
- structured knowledge graph of statutes + case relationships
- automatic citation verification from official court APIs
- multilingual drafting templates
- feedback-driven learning with safe evaluation pipelines

---
