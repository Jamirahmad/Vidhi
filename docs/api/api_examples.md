# API Examples — Vidhi

This document provides example API requests and responses for Vidhi’s FastAPI-based endpoints.

> **Note:** These examples are for development/testing only. Vidhi is a research assistant and does not provide legal advice.

---

## Base URL

Local development:

```bash
http://127.0.0.1:8000
```

## Health Check
### Request
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

### Response (200)
```json
{
  "status": "ok",
  "service": "vidhi-api",
  "version": "0.1.0"
}
```

## Submit Case Intake
### Endpoint
```POST /api/v1/intake```

### Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/intake" \
  -H "Content-Type: application/json" \
  -d '{
    "case_title": "Bail Application - NDPS Act",
    "case_facts": "The accused was arrested with 50 grams of contraband. No independent witness was present.",
    "jurisdiction": "Maharashtra High Court",
    "case_type": "criminal",
    "language": "en"
  }'
```

### Response (200)
```json
{
  "case_id": "VIDHI-CASE-2026-00012",
  "message": "Case intake recorded successfully.",
  "next_step": "Run research workflow"
}
```

## Run Research Workflow
### Endpoint
```POST /api/v1/research```

### Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/research" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "VIDHI-CASE-2026-00012",
    "query": "Bail under NDPS Act, procedural lapses, lack of independent witness",
    "top_k": 5
  }'
```

### Response (200)
```json
{
  "case_id": "VIDHI-CASE-2026-00012",
  "research_summary": "Found 5 relevant precedents related to NDPS bail, procedural compliance, and evidentiary issues.",
  "citations": [
    {
      "court": "Supreme Court of India",
      "case_name": "State vs XYZ",
      "citation": "AIR 2018 SC 1234",
      "url": "https://example.com/case1"
    }
  ],
  "warnings": [
    "All citations must be verified from official sources before use."
  ]
}
```

## Generate Arguments (Supporting + Counter)
### Endpoint
```POST /api/v1/arguments```

### Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/arguments" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "VIDHI-CASE-2026-00012",
    "facts": "Accused arrested with contraband. No independent witness.",
    "sections": ["NDPS Act Section 37", "CrPC Section 439"]
  }'
```

### Response (200)
```json
{
  "case_id": "VIDHI-CASE-2026-00012",
  "supporting_arguments": [
    "Procedural non-compliance reduces evidentiary reliability.",
    "Absence of independent witnesses creates reasonable doubt."
  ],
  "counter_arguments": [
    "Quantity indicates seriousness of offence.",
    "Section 37 requires strict satisfaction before granting bail."
  ],
  "note": "Arguments are generated for research support only and require human verification."
}
```

## Generate Legal Document Draft
### Endpoint
```POST /api/v1/documents/generate```

### Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "VIDHI-CASE-2026-00012",
    "document_type": "bail_application",
    "language": "en",
    "include_citations": true
  }'
```

### Response (200)
```json
{
  "case_id": "VIDHI-CASE-2026-00012",
  "document_type": "bail_application",
  "output_path": "outputs/generated_documents/VIDHI-CASE-2026-00012_bail_application.md",
  "message": "Draft generated successfully. Review required."
}
```

## Run Compliance Check
### Endpoint
```POST /api/v1/compliance/check```

### Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/compliance/check" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "VIDHI-CASE-2026-00012",
    "document_path": "outputs/generated_documents/VIDHI-CASE-2026-00012_bail_application.md",
    "court": "Bombay High Court"
  }'
```

### Response (200)
```json
{
  "case_id": "VIDHI-CASE-2026-00012",
  "court": "Bombay High Court",
  "compliance_status": "needs_review",
  "issues_found": [
    "Missing annexure list",
    "Citation format needs manual verification"
  ],
  "suggested_fixes": [
    "Add Annexure A, Annexure B sections",
    "Verify citation authenticity from official sources"
  ]
}
```

## Submit Feedback (Human-in-the-loop)
### Endpoint
```POST /api/v1/feedback```

### Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "VIDHI-CASE-2026-00012",
    "agent": "DocComposer",
    "feedback_type": "correction",
    "message": "Document draft is good, but needs stronger limitation section.",
    "rating": 4
  }'
```

### Response (200)
```json
{
  "status": "received",
  "message": "Feedback stored successfully."
}
```

## Error Example (Validation Failure)
### Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/research" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Response (422)
```json
{
  "detail": [
    {
      "loc": ["body", "case_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Authentication Example (Future)
Vidhi currently runs in open mode for local development.

In production, recommended options include:
- API Key header authentication
- OAuth2 with JWT
- IAM-based access controls (AWS)
Example (API Key header):
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/research" \
  -H "X-API-KEY: <your-key>"
```

## Notes on Safe Usage
- Vidhi does **not** provide legal advice.
- All citations must be verified from authentic sources.
- Human review is mandatory before court submission.
-Outputs may contain incomplete or outdated information.

## OpenAPI Documentation
Once the API is running, access Swagger UI:
```bash
http://127.0.0.1:8000/docs
```
And OpenAPI JSON spec:
```bash
http://127.0.0.1:8000/openapi.json
```
