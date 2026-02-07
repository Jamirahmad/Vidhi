# Evaluation Strategy

This document defines how **Vidhi** evaluates accuracy, reliability, citation correctness, hallucination risk, and overall system performance across the end-to-end multi-agent workflow.

Vidhi is a **legal research + drafting assistant**, therefore evaluation must prioritize:

- **Citation correctness**
- **Faithfulness to retrieved sources**
- **Court-specific compliance**
- **Non-hallucination guarantees**
- **Human verification checkpoints**
- **Reproducibility of outputs**

---

## 1. Why Evaluation Matters in Vidhi

Legal AI systems fail primarily due to:

- Hallucinated case laws or fabricated citations
- Wrong sections applied (IPC/CrPC/CPC errors)
- Missing jurisdiction-specific rules
- Poor precedent selection (irrelevant or outdated)
- Incorrect limitation period assumptions
- Drafting outputs that look convincing but are legally invalid

Vidhi addresses this by applying **multi-layer evaluation** at:

- Retrieval layer (vectorstore results)
- Reasoning layer (agent outputs)
- Drafting layer (final documents)
- Compliance layer (formatting + annexures)
- Human-in-the-loop verification

---

## 2. Evaluation Objectives

Vidhi’s evaluation framework is designed to measure:

### 2.1 Retrieval Quality
- Are the retrieved judgments relevant?
- Are they jurisdictionally correct?
- Are they recent and authoritative?
- Are they Supreme Court / binding judgments when required?

### 2.2 Output Faithfulness
- Are claims grounded in retrieved text?
- Are citations accurate and verifiable?
- Is any content invented?

### 2.3 Drafting Quality
- Is the document structured correctly?
- Does it include mandatory sections?
- Does it align with common Indian court formats?

### 2.4 Compliance and Safety
- Are ethical disclaimers included?
- Are legal opinions avoided?
- Is the human verification step enforced?

---

## 3. Key Evaluation Dimensions

Vidhi evaluates outputs across these core dimensions:

| Dimension | What it Measures | Why it Matters |
|----------|------------------|----------------|
| **Relevance** | How closely results match the query facts/issues | Avoids irrelevant precedents |
| **Authority** | SC/HC precedence strength and applicability | Ensures correct legal weight |
| **Faithfulness** | Whether the model output is grounded in sources | Prevents hallucinations |
| **Citation Accuracy** | Correct case title, year, court, citation | Prevents fake citations |
| **Completeness** | Coverage of all major issues and required clauses | Reduces missing arguments |
| **Clarity** | Readability of arguments and drafts | Helps junior lawyers and litigants |
| **Compliance** | Court format + annexures + fees checklist | Reduces rejection risk |
| **Safety & Ethics** | Avoiding legal advice / fabricated law | Prevents harmful usage |

---

## 4. Agent-Level Evaluation

Each agent is evaluated separately before measuring full workflow performance.

### 4.1 CaseFinder (Retrieval Evaluation)

**What to test**
- Top-K retrieval relevance
- Source diversity (SC + HC + tribunals)
- Correct jurisdiction match

**Metrics**
- Precision
- Recall
- Mean Reciprocal Rank (MRR)
- Coverage score (did it retrieve at least 1 binding authority?)

**Example test**
Input: *Bail application under NDPS Act, Mumbai jurisdiction*  
Expected: NDPS bail judgments from Supreme Court and Bombay High Court.

---

### 4.2 IssueSpotter (Issue Extraction Evaluation)

**What to test**
- Correct extraction of legal issues
- Correct identification of applicable sections (IPC/CrPC/CPC)

**Metrics**
- Issue match score (manual rubric)
- Section accuracy score (exact match)
- Missing issue rate

**Test method**
- Compare extracted issues vs human-labeled dataset

---

### 4.3 LimitationChecker (Time-bar Accuracy Evaluation)

**What to test**
- Correct limitation period identification
- Correct handling of exceptions (condonation, Section 5, Section 18 etc.)

**Metrics**
- Limitation accuracy (%)
- False positive time-bar rate
- False negative time-bar rate

**Test method**
- Use pre-built limitation scenarios with known answers

---

### 4.4 ArgumentBuilder (Reasoning Evaluation)

**What to test**
- Argument consistency
- Use of retrieved precedents
- Inclusion of counter-arguments

**Metrics**
- Grounded argument ratio (claims backed by sources)
- Contradiction handling score
- Persuasiveness score (human rubric)

---

### 4.5 DocComposer (Draft Quality Evaluation)

**What to test**
- Draft structure correctness
- Completeness of mandatory clauses
- Legal drafting tone and clarity

**Metrics**
- Structural completeness score
- Readability score (Flesch or custom rubric)
- Missing mandatory clause count

**Test method**
- Compare drafts with sample court templates

---

### 4.6 ComplianceGuard (Court Compliance Evaluation)

**What to test**
- Formatting checklist correctness
- Annexure and affidavit requirements
- Court-specific submission rules

**Metrics**
- Compliance checklist pass rate
- Missing annexure count
- Formatting error count

---

### 4.7 AidConnector (Legal Aid Suggestions Evaluation)

**What to test**
- Correct suggestion of legal aid resources
- Proper region-specific relevance
- No misleading advice

**Metrics**
- Coverage of valid aid sources
- Incorrect suggestion rate

---

## 5. End-to-End Workflow Evaluation

Vidhi’s complete workflow is evaluated using scenario-driven testing.

### 5.1 Scenario-Based Test Cases

Vidhi uses predefined scenarios such as:

- Bail application under IPC/CrPC
- NDPS bail strict conditions
- Domestic violence complaint response
- Consumer court dispute drafting
- Civil injunction filing
- Motor accident claim petition
- Cheque bounce notice (NI Act 138)
- Employment dispute (tribunal)

Each scenario includes:
- Facts
- Jurisdiction
- Expected legal issues
- Expected precedent types
- Draft output expectations

---

## 6. Hallucination Detection Strategy

Hallucination is the **highest risk** in legal systems.

Vidhi enforces hallucination checks using multiple layers:

### 6.1 Citation Existence Validation
- Every cited case must map to a real source record
- Citation must match:
  - Case name
  - Court name
  - Year
  - Judgment ID / URL (if available)

If not found → output flagged as **INVALID**.

### 6.2 Source-Grounded Answer Enforcement
Agents must attach:
- Source snippet
- Paragraph reference
- Link/identifier (if available)

No source → claim is rejected.

### 6.3 Confidence Scoring
Each agent assigns a confidence score:
- High (direct citation match)
- Medium (partial match)
- Low (no citation / inferred)

Low confidence triggers:
- human handoff
- warning banner

### 6.4 Contradiction Checks
ArgumentBuilder runs a contradiction scan:
- supporting precedents vs contradictory precedents
- outputs must explicitly mention contradictions

### 6.5 Guardrail Prompts
DocComposer and ArgumentBuilder prompts include:
- “If you do not know, say UNKNOWN”
- “Do not invent case law or citations”
- “Only use retrieved sources”

---

## 7. Human Verification as a Mandatory Evaluation Layer

Vidhi enforces a **Human-in-the-Loop (HITL)** checkpoint.

### 7.1 Human Handoff Rules
Handoff triggers when:
- Confidence score < threshold
- No Supreme Court authority found (when required)
- Conflicting precedents exist
- Limitation unclear
- Draft includes any uncertain assumptions

### 7.2 Human Reviewer Checklist
Reviewer validates:
- Citation correctness
- Legal section applicability
- Jurisdiction match
- Argument strength
- Court formatting

---

## 8. Evaluation Metrics (System-Level KPIs)

### 8.1 Retrieval Metrics
- Precision@5, Precision@10
- Recall@10
- MRR (Mean Reciprocal Rank)
- Coverage of binding authority (% scenarios with SC judgment)

### 8.2 Draft Quality Metrics
- Clause completeness (% mandatory clauses included)
- Formatting compliance score
- Human acceptance rate

### 8.3 Hallucination Metrics
- Hallucination rate (fabricated citations / total citations)
- Unsupported claim rate
- Citation mismatch rate

### 8.4 Efficiency Metrics
- Time-to-draft reduction
- Agent runtime (latency per agent)
- End-to-end workflow time

### 8.5 User Experience Metrics
- User satisfaction rating
- “Useful precedent found” rate
- “Draft usable with edits” rate

---

## 9. Testing Methodology

Vidhi uses 4 types of testing:

### 9.1 Unit Testing
Each agent has unit tests:
- input validation
- prompt output structure validation
- schema checks

### 9.2 Integration Testing
Test complete agent chains:
- Orchestrator → CaseFinder → IssueSpotter → ... → ComplianceGuard

### 9.3 Regression Testing
Whenever prompts or retrieval logic changes:
- rerun benchmark scenario set
- compare output scores
- detect drift

### 9.4 Manual Expert Review
Periodic review by:
- lawyers
- legal interns
- compliance specialists

Manual review is required to validate legal realism.

---

## 10. Test Dataset Strategy

Vidhi maintains datasets in `/data/evaluation/`:

- **golden_cases.json** (human-labeled case facts + expected outcomes)
- **golden_citations.csv** (verified citations for retrieval testing)
- **templates/** (court formats for compliance testing)

### 10.1 Golden Dataset Creation
Dataset includes:
- diverse courts (SC + multiple HCs)
- diverse domains (civil, criminal, consumer, tribunal)
- mixed complexity (simple to ambiguous)

---

## 11. Benchmarking Approach

### 11.1 Baseline Benchmark
Compare Vidhi performance against:
- manual keyword search
- Google + SCC Online style retrieval simulation
- single-agent RAG baseline

### 11.2 Improvement Benchmark
Vidhi should demonstrate:
- reduced hallucination rate
- improved retrieval relevance
- faster drafting turnaround
- improved human acceptance rate

---

## 12. Evaluation Tools and Platforms

Recommended tools aligned to the course syllabus:

- **pytest** → unit tests
- **LangSmith / PromptLayer** → tracing and evaluation
- **ChromaDB / FAISS metrics** → retrieval evaluation
- **Pandas** → benchmark scoring and reporting
- **Streamlit dashboard** → evaluation visualization
- **GitHub Actions** → automated evaluation pipelines

---

## 13. Success Criteria for Capstone

Vidhi is considered successful if it achieves:

### Minimum Success Metrics
- ≥ 80% citation validity rate
- ≤ 5% hallucinated citation rate
- ≥ 70% relevance score in top-5 retrieval
- ≥ 60% draft acceptance (usable with edits)
- 30–50% reduction in drafting time compared to manual drafting

### Stretch Success Metrics
- ≥ 90% citation validity rate
- ≤ 2% hallucinated citation rate
- ≥ 85% relevance score in top-5 retrieval
- ≥ 75% human acceptance rate

---

## 14. Reporting Evaluation Results

Vidhi stores evaluation results under:

```
/reports/evaluation/
    retrieval_metrics.csv
    hallucination_report.json
    scenario_scores.csv
    compliance_checklist_report.csv
```

### Evaluation Report Summary Template
Each evaluation run produces:
- Total scenarios tested
- Retrieval performance summary
- Hallucination incidents summary
- Draft acceptance score
- Compliance checklist pass rate
- Improvement vs baseline

---

## 15. Continuous Improvement Loop

Vidhi uses evaluation results to improve:

- prompt templates
- retrieval chunking strategy
- embeddings model selection
- agent memory design
- compliance rules
- court-specific drafting templates

Evaluation is treated as an iterative loop:
**Test → Measure → Fix → Retest → Deploy**

---

## 16. Disclaimer

Vidhi is an assistive system designed for legal research and drafting workflows.

- It does not provide legal advice.
- It cannot guarantee correctness of outcomes.
- All outputs must be reviewed by a qualified lawyer before filing.

---

## 17. Next Planned Enhancements (Future Scope)

- Automated judgment summarization quality scoring
- Multi-lingual evaluation benchmark datasets
- Court-specific compliance scoring models
- Red-team hallucination stress testing
- Automated citation cross-check with official court databases

---

## 18. References

- Supreme Court of India official portal
- High Court portals (state-wise)
- Indian Kanoon / SCC Online style search workflows
- LangSmith evaluation tools
- OpenAI / embedding model benchmarking methods

---

**File:** `docs/EVALUATION.md`
