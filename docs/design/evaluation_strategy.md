# Evaluation Strategy

## Objective
The evaluation strategy for **Vidhi** ensures accuracy, reliability, safety, and usefulness of outputs produced by the multi-agent legal research and document automation system. Given the legal domain’s sensitivity, evaluation prioritizes correctness, traceability, and human verifiability over automation speed.

---

## Evaluation Dimensions

### 1. Retrieval Quality
Measures how effectively relevant case laws and statutes are retrieved.

**Metrics**
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Coverage across courts (SC / HC / Tribunals)

**Validation**
- Gold-standard curated legal queries
- Manual relevance scoring by domain reviewers

---

### 2. Citation Accuracy
Ensures that all generated outputs reference valid and traceable sources.

**Checks**
- Citation format validation
- Source document existence
- Paragraph-level citation mapping

**Failure Handling**
- Missing or unverifiable citations trigger human review
- Outputs flagged as “Draft – Review Required”

---

### 3. Hallucination Detection
Prevents fabricated cases, statutes, or legal reasoning.

**Techniques**
- Retrieval-grounded generation only
- Cross-agent consistency checks
- Post-generation citation validation

**Automated Tests**
- Zero-citation response detection
- Unsupported claim identification

---

### 4. Agent-Level Performance
Each agent is evaluated independently and as part of workflows.

| Agent | Key Evaluation Criteria |
|------|------------------------|
| CaseFinder | Recall, relevance, court coverage |
| IssueSpotter | Section identification accuracy |
| LimitationChecker | Rule correctness |
| ArgumentBuilder | Logical consistency |
| DocComposer | Structural completeness |
| ComplianceGuard | Filing rule adherence |
| AidConnector | Eligibility correctness |

---

### 5. End-to-End Workflow Validation
Tests realistic legal scenarios.

**Scenarios**
- Bail application
- Property dispute
- Consumer complaint

**Success Criteria**
- All mandatory steps executed
- Human handoff triggered where required
- No unsafe or advisory outputs

---

### 6. Latency & Cost Monitoring
Ensures suitability for free-tier deployment.

**Metrics**
- Agent execution time
- API call count
- Vector search latency

---

## Human-in-the-Loop Review

Mandatory human review is enforced when:
- Citations are incomplete
- Conflicting precedents exist
- Novel legal questions arise
- Ethical or safety flags are raised

Human feedback is logged for future evaluation improvement.

---

## Continuous Improvement Loop
1. Capture user feedback
2. Analyze failure patterns
3. Update prompts, retrieval, or rules
4. Re-run evaluation benchmarks

---

## Evaluation Artifacts
- Evaluation reports
- Metric dashboards
- Agent trace logs
- Failure analysis summaries

---

## Ethical Alignment
Evaluation explicitly checks for:
- No legal advice generation
- No fabricated content
- Transparency of uncertainty

---

## Summary
Vidhi’s evaluation framework balances automation with accountability, ensuring outputs remain assistive, auditable, and legally responsible.

