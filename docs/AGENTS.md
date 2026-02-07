# Vidhi — Agents Reference Guide (Responsibilities, Inputs/Outputs, Human Handoff Rules)

Vidhi is a **multi-agent legal research and document automation platform** designed for the Indian legal ecosystem.  
This document provides a complete reference of all agents in the Vidhi system, including:

- Responsibilities and scope of each agent
- Input and output contract (expected fields)
- Tooling and dependencies used by each agent
- Human handoff rules and safety boundaries

This is intended to be the **single source of truth** for agent design and collaboration.

---

## Agent Design Principles

Vidhi agents follow these principles:

1. **Single Responsibility**  
   Each agent performs one core function.

2. **Structured I/O**  
   Each agent must accept and return predictable JSON-like structured outputs.

3. **Traceability & Citations**  
   Any legal claim must be supported by citations whenever possible.

4. **Human-in-the-Loop Safety**  
   Vidhi never replaces a lawyer. All outputs are drafts requiring review.

5. **No Fabrication Rule**  
   Agents must not hallucinate case laws, citations, sections, or legal provisions.

6. **Orchestrator-Controlled Execution**  
   Agents cannot directly invoke other agents; all communication flows via the orchestrator.

---

## Agents Overview (Quick Table)

| Agent Code | Friendly Name | File | Primary Responsibility |
|-----------|---------------|------|------------------------|
| **LRA** | LegalOrchestrator | `src/core/orchestrator.py` | Manages workflow and coordinates all agents |
| **CLSA** | CaseFinder | `src/agents/clsa_case_law_search_agent.py` | Retrieves relevant judgments and precedents |
| **LII** | IssueSpotter | `src/agents/lii_issue_identifier_agent.py` | Identifies legal issues and relevant sections |
| **LAA** | LimitationChecker | `src/agents/laa_limitation_analysis_agent.py` | Analyzes limitation and time-bar applicability |
| **LAB** | ArgumentBuilder | `src/agents/lab_argument_builder_agent.py` | Builds arguments and counter-arguments |
| **DGA** | DocComposer | `src/agents/dga_document_generation_agent.py` | Drafts petitions, notices, affidavits, etc. |
| **CCA** | ComplianceGuard | `src/agents/cca_compliance_check_agent.py` | Checks filing compliance, formatting, annexures |
| **LAF** | AidConnector | `src/agents/laf_legal_aid_finder_agent.py` | Suggests legal aid and pro-bono options |

> Note: The orchestrator is technically not an "agent" in the same sense, but it is treated as the controller of all agent workflows.

---

# Shared Input Contract (Case Intake Schema)

All workflows begin with a common structured input, typically collected via UI/API.

### Required Inputs

```json
{
  "case_facts": "Text describing the full case narrative",
  "jurisdiction": "State + Court (example: Delhi High Court)",
  "case_type": "civil | criminal | tribunal",
  "language": "en | hi | mr | ta | te | kn | gu | bn"
}
```
### Optional Inputs
```json
{
  "known_sections": ["IPC 420", "CrPC 437"],
  "case_stage": "FIR | Investigation | Trial | Appeal | Revision | Bail",
  "timeline": {
    "incident_date": "YYYY-MM-DD",
    "complaint_date": "YYYY-MM-DD"
  },
  "relief_sought": "Bail | Refund | Injunction | Quashing | Compensation",
  "party_details": {
    "petitioner": "Name",
    "respondent": "Name"
  }
}
```

---

## Shared Output Contract (Final Orchestrator Response)
The final output returned to the user should always contain:

```json
{
  "research_summary": "...",
  "legal_issues": ["..."],
  "sections_identified": ["..."],
  "case_law_citations": [
    {
      "case_name": "...",
      "court": "...",
      "year": "...",
      "citation": "...",
      "relevance_reason": "..."
    }
  ],
  "arguments": {
    "supporting": ["..."],
    "counter": ["..."]
  },
  "generated_documents": [
    {
      "document_type": "Bail Application",
      "file_path": "outputs/generated_documents/bail_application.md"
    }
  ],
  "compliance_report": {
    "missing_items": ["..."],
    "court_fee_estimate": "...",
    "formatting_issues": ["..."]
  },
  "legal_aid_options": ["..."],
  "human_review_required": true,
  "disclaimer": "Vidhi does not provide legal advice..."
}
```

---

## Agent Details
### 1. LegalOrchestrator (LRA)
**Agent Role:** Workflow Orchestrator & Control Tower
**Module:** ```src/core/orchestrator.py```

#### Responsibilities
- Acts as the central controller for all workflows
- Validates case intake inputs
- Decides execution plan based on case type and jurisdiction
- Routes tasks to correct agents in correct order
- Ensures safe prompting and structured output formatting
- Maintains session memory and execution traces
- Enforces human review and ethical safeguards

#### Inputs
- Full case intake schema
- User preferences (language, output format)
- Configuration settings (embedding store type, API keys)

#### Outputs
- Final compiled report combining all agents’ outputs
- Unified structured response object
- Final list of recommended documents to generate

#### Dependencies / Tools
- Prompt Manager
- Task Router
- Safety Guardrails
- Session Memory
- Citation Validator
- Response Formatter

#### Human Handoff Rules
The orchestrator must ALWAYS mark outputs as draft and require human review when:

- any legal conclusion is implied
- any citation confidence is low
- jurisdiction rules are unclear
- limitation analysis is uncertain

### 2. CaseFinder (CLSA — Case Law Search Agent)
**Agent Role:** Case Law Retrieval Specialist
**Module:** ```src/agents/clsa_case_law_search_agent.py```

#### Responsibilities
- Searches relevant case laws and precedents
- Retrieves judgments from Supreme Court, High Courts, tribunals
- Performs semantic similarity search using embeddings
- Returns top-ranked judgments with metadata
- Identifies both supporting and contradictory precedents
- Prioritizes jurisdiction-matching citations

#### Inputs
```json
{
  "case_facts": "...",
  "jurisdiction": "...",
  "case_type": "...",
  "keywords": ["fraud", "bail", "property dispute"],
  "sections_identified": ["IPC 420", "CrPC 439"]
}
```

#### Outputs
```json
{
  "retrieved_cases": [
    {
      "case_name": "...",
      "court": "...",
      "year": "...",
      "citation": "...",
      "url": "...",
      "summary": "...",
      "relevance_score": 0.87,
      "key_paragraphs": ["..."]
    }
  ],
  "search_notes": "..."
}
```

#### Dependencies / Tools
- Vector Store (FAISS/ChromaDB)
- Embedding Provider
- Retriever and Reranker
- Optional external connectors (Indian Kanoon, SC/HC portals)

#### Human Handoff Rules
Must escalate to human when:
- citations cannot be verified
- retrieval confidence is low (score < threshold)
- only partial judgments are available
- contradictory cases exist with unclear applicability

---

### 3. IssueSpotter (LII — Legal Issue Identifier Agent)
**Agent Role:** Legal Issue Extraction Specialist
**Module:** ```src/agents/lii_issue_identifier_agent.py```

#### Responsibilities
- Extracts legal issues from case facts
- Identifies applicable laws/sections (IPC, CrPC, CPC, special acts)
- Identifies case type classification
- Detects key entities (accused, complainant, judge, property, dates)
- Extracts timeline and key events
- Highlights missing information needed for proper drafting

#### Inputs
```json
{
  "case_facts": "...",
  "case_type": "...",
  "jurisdiction": "..."
}
```

#### Outputs
```json
{
  "legal_issues": ["Fraud", "Breach of contract", "Cheating"],
  "sections_identified": ["IPC 420", "IPC 468", "CrPC 439"],
  "case_domain": "bail",
  "missing_information": ["Exact FIR number", "Police station details"],
  "key_entities": {
    "petitioner": "...",
    "respondent": "...",
    "incident_location": "..."
  }
}
```

#### Dependencies / Tools
- Prompt Templates
- Legal rules dictionary (optional)
- Named entity extraction (optional)

#### Human Handoff Rules
Must ask for human clarification if:
- key facts are missing (dates, place, FIR)
- jurisdiction mismatch is detected
- conflicting case facts are present

---

### 4. LimitationChecker (LAA — Limitation Analysis Agent)
**Agent Role:** Limitation & Time-Bar Analysis Specialist
**Module:** ```src/agents/laa_limitation_analysis_agent.py```

#### Responsibilities
- Checks whether a case is time-barred under Limitation Act principles
- Determines applicable limitation period based on case type
- Identifies exceptions (acknowledgment, fraud discovery, condonation)
- Flags risks related to delay, laches, and maintainability
- Provides structured reasoning with confidence tags

#### Inputs
```json
{
  "case_facts": "...",
  "timeline": {
    "incident_date": "YYYY-MM-DD",
    "acknowledgment_date": "YYYY-MM-DD"
  },
  "case_type": "civil"
}
```

#### Outputs
```json
{
  "limitation_status": "Likely within limitation",
  "limitation_risk_level": "medium",
  "reasoning": [
    "Section 18 acknowledgment revives limitation",
    "Written promise in 2025 supports fresh limitation start"
  ],
  "human_verification_required": true
}
```

#### Dependencies / Tools
- Timeline extraction logic
- Legal limitation rules database (optional)
- Prompt templates

#### Human Handoff Rules
Must escalate when:
- dates are unclear or missing
- multiple limitation interpretations exist
- special act limitations apply (consumer, tax, service law)

---

### 5. ArgumentBuilder (LAB — Legal Argument Builder Agent)
**Agent Role:** Argument Generation Specialist
**Module:** ```src/agents/lab_argument_builder_agent.py```

#### Responsibilities
- Creates structured legal arguments aligned to the case facts
- Generates counter-arguments and rebuttal strategy
- Links arguments with citations from retrieved case law
- Identifies strongest and weakest points in the case
- Suggests legal strategy but avoids legal opinion

#### Inputs
```json
{
  "legal_issues": ["Fraud", "Cheating"],
  "sections_identified": ["IPC 420"],
  "retrieved_cases": [...],
  "jurisdiction": "Delhi High Court"
}
```

### Outputs
```json
{
  "supporting_arguments": [
    {
      "argument": "Bail is the rule, jail is the exception",
      "citations": ["Sanjay Chandra v. CBI (2012)"]
    }
  ],
  "counter_arguments": [
    {
      "argument": "Economic offenses are serious and require stricter scrutiny",
      "citations": ["..."]
    }
  ],
  "risk_flags": ["Flight risk argument may be raised by prosecution"]
}
```
#### Dependencies / Tools
- Citation validator
- Prompt templates
- Output formatting rules

#### Human Handoff Rules
Must escalate if:
- argument suggests guaranteed outcome
- citations are weak or missing
- contradictory precedent exists without resolution

---

### 6. DocComposer (DGA — Document Generation Agent)
**Agent Role:** Legal Drafting Specialist
**Module:** ```src/agents/dga_document_generation_agent.py```

#### Responsibilities'
- Drafts legal documents based on templates
- Produces petitions, bail applications, legal notices, affidavits, suits
- Ensures proper structure: facts, grounds, prayers, annexures
- Inserts citations and legal provisions in relevant sections
- Supports multilingual output generation

#### Inputs
```json
{
  "document_type": "Bail Application",
  "case_facts": "...",
  "arguments": {...},
  "citations": [...],
  "jurisdiction": "Delhi High Court"
}
```

#### Outputs
```json
{
  "document_type": "Bail Application",
  "draft_text": "... full legal draft ...",
  "output_file": "outputs/generated_documents/bail_application.md",
  "placeholders_remaining": ["Petitioner Name", "FIR Number"]
}
```

#### Dependencies / Tools
- Template library: ```src/prompts/templates/```
- Translation libraries (optional)
- Markdown/PDF conversion utilities

#### Human Handoff Rules
Document drafts must always include:
- "DRAFT - FOR LAWYER REVIEW ONLY"
- Placeholder fields clearly marked
- Citation list attached separately
Must escalate when:
- required facts are missing
- drafting requires court-specific formatting rules not present
- legal strategy conflicts are detected

---

### 7. ComplianceGuard (CCA — Compliance Check Agent)
**Agent Role:** Filing Readiness & Compliance Validator
**Module:** ```src/agents/cca_compliance_check_agent.py```

#### Responsibilities
- Validates that generated document meets filing expectations
- Checks annexures checklist
- Verifies court fee estimation requirements
- Ensures citations appear correctly formatted
- Flags missing affidavits, vakalatnama, verification sections
- Ensures structure matches expected court drafting norms

#### Inputs
```json
{
  "document_type": "Civil Suit",
  "draft_text": "...",
  "jurisdiction": "Pune District Court",
  "case_type": "civil"
}
```

#### Outputs
```json
{
  "compliance_status": "Incomplete",
  "missing_items": ["Affidavit", "Court fee stamp", "Annexure A"],
  "formatting_issues": ["Prayer section missing", "Verification clause missing"],
  "court_fee_estimate": "₹15,000 (approx)",
  "final_ready_for_filing": false
}
```

#### Dependencies / Tools
- Compliance rule checklists
- Citation validator
- Formatting rule engine (optional)

#### Human Handoff Rules
Must ALWAYS require human review before finalization because:
- court requirements vary widely
- filing rules depend on local practice
- stamp duty and fee rules may change

---

### 8. AidConnector (LAF — Legal Aid Finder Agent)
**Agent Role:** Legal Aid & Support Resource Finder
**Module:** ```src/agents/laf_legal_aid_finder_agent.py```

#### Responsibilities
- Suggests free or affordable legal aid options
- Provides information about DLSA/SLSA services
- Suggests NGOs and pro-bono groups
- Provides relevant contact details or web references (if available)
- Helps self-representing litigants find guidance resources

#### Inputs
```json
{
  "jurisdiction": "Pune, Maharashtra",
  "case_type": "civil",
  "user_type": "litigant"
}
```

#### Outputs
```json
{
  "legal_aid_options": [
    {
      "organization": "District Legal Services Authority (DLSA Pune)",
      "type": "Government Legal Aid",
      "notes": "Provides free legal support to eligible individuals"
    }
  ],
  "recommended_next_steps": ["Visit DLSA office with identity proof"]
}
```

#### Dependencies / Tools
- Static dataset of legal aid resources
- Optional web connectors (future scope)

#### Human Handoff Rules
If the agent cannot verify contact details, it must:
- provide general guidance only
- ask user to confirm via official websites

---

### Human Handoff Rules (Global)
Vidhi is **not a lawyer**. The system must always enforce human review before legal use.

#### Mandatory Human Review Triggers
Human verification is REQUIRED if any of the following occurs:

#### Legal Advice Risk
- Output contains strong recommendations like "You should definitely file"
- Output implies guaranteed outcomes ("Bail will be granted")
- Output states a final legal opinion

#### Unverified Citations
- Case citations are incomplete
- Court/year is missing
- Citation format cannot be validated
- Retrieval confidence is low

#### Jurisdictional Uncertainty
- Court rules differ (HC vs District Court)
- Special tribunals involved (NCLT, CAT, ITAT, consumer forum)

#### Sensitive / High-Risk Matters
- domestic violence, sexual offenses, POCSO
- terrorism / UAPA / NSA
- matters involving minors or protected identities

#### Ethical Conflicts
- user requests illegal strategy
- conflicting interests detected
- user asks to hide facts or fabricate evidence

---

### What Vidhi Must NEVER Do
Vidhi must not:
- fabricate judgments, citations, or sections
- create fake evidence or fake FIR numbers
- provide binding legal advice
- instruct illegal actions
- replace lawyer judgment or filing responsibility

---

### Agent Output Formatting Rules
All agents must output:
- **Structured format** (JSON-like)
- Citations included in a list (if referenced)
- Confidence label: ```high | medium | low```
- A clear ```human_review_required``` flag
Example:
```json
{
  "confidence": "medium",
  "human_review_required": true,
  "notes": "Draft is based on retrieved precedents. Verify citation authenticity before filing."
}
```

### Agent Execution Order (Default Workflow)
This is the default pipeline executed by the orchestrator:
1. **IssueSpotter (LII)** → Extract issues and sections
2. **CaseFinder (CLSA)** → Retrieve relevant precedents
3. **Legal Research Agent (LRA)** → Summarize and structure findings
4. **LimitationChecker (LAA)** → Check limitation/time-bar
5. **ArgumentBuilder (LAB)** → Build arguments/counter-arguments
6. **DocComposer (DGA)** → Generate document drafts
7. **ComplianceGuard (CCA)** → Validate compliance
8. **AidConnector (LAF)** → Suggest legal aid if needed

---

### Related Documentation
For deeper design references:
- ```docs/ARCHITECTURE.md```
- ```docs/design/agent_responsibilities.md```
- ```docs/design/human_handoff_rules.md```
- ```docs/design/safety_ethics_governance.md```
- ```docs/design/evaluation_strategy.md```

### Disclaimer
Vidhi is a research and drafting assistant.
It does not provide legal advice, and all outputs must be reviewed and validated by a qualified legal professional before use.

This repository is for educational and research purposes only.
