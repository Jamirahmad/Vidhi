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
