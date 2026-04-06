# Vidhi API Documentation

Base URL (local): `http://localhost:8000`

All endpoints return JSON unless explicitly noted.

## Conventions

- **Versioned prefix:** `/api/v1`
- **Validation:** request bodies are validated via Pydantic models.
- **Error format:**

```json
{
  "error": "Human-readable server error",
  "code": "MACHINE_CODE",
  "userMessage": "Safe user-facing message"
}
```

---

## 1) Health & feedback

### `GET /api/v1/health`
Returns backend readiness, model/provider metadata, middleware flags, and knowledge availability.

**Sample response**
```json
{
  "status": "ok",
  "provider": "openrouter",
  "model": "openai/gpt-4.1-mini",
  "apiKeyConfigured": true,
  "knowledge": {
    "provider": "langchain-chroma",
    "seedPath": ".../backend/data/knowledge",
    "publicSource": "https://www.sci.gov.in/",
    "available": true,
    "error": null
  },
  "middleware": {
    "exceptionHandler": true,
    "requestLogger": true,
    "securityHeaders": true,
    "rateLimiter": {
      "enabled": true,
      "windowSeconds": 60,
      "maxRequests": 120,
      "bypassPaths": ["/api/v1/health"]
    }
  }
}
```

### `POST /api/v1/feedback`
Stores arbitrary feedback payload.

**Request body** (schema is flexible)
```json
{
  "screen": "issue-spotter",
  "rating": 4,
  "comment": "Helpful draft, needed more citations"
}
```

**Response**
```json
{
  "status": "received",
  "feedbackId": "9f7f8a0a-..."
}
```

### `GET /api/v1/feedback?limit=50`
Returns latest feedback entries.

---

## 2) Knowledge base

### `GET /api/v1/knowledge-base/search`
Searches local knowledge store.

**Query params**
- `q` (required, min length 2)
- `limit` (optional, default 12, range 1..50)

### `POST /api/v1/knowledge-base/refresh`
Refreshes public case corpus.

**Query params**
- `years` (default 5, range 1..10)
- `limit` (default 200, range 10..500)

### `POST /api/v1/knowledge-base/live-search`
Performs web/live search or provision-focused hybrid search.

**Request body**
```json
{
  "query": "section 420 ipc cheating",
  "intent": "case_law",
  "limit": 10
}
```

**Sample response (shape)**
```json
{
  "query": "section 420 ipc cheating",
  "intent": "case_law",
  "results": [
    {
      "id": "source-id",
      "intent": "case_law",
      "title": "Case title",
      "snippet": "Short summary",
      "url": "https://...",
      "domain": "example.org",
      "publishedAt": "",
      "source": "searchapi"
    }
  ],
  "count": 1,
  "source": "searchapi",
  "sourceBreakdown": {"searchapi": 1},
  "diagnostics": {
    "webConfigured": true,
    "webProvider": "searchapi",
    "webFetchedCount": null,
    "webError": ""
  }
}
```

### `POST /api/v1/knowledge-base/live-search/drilldown`
Builds source-grounded analysis from selected references.

**Request body**
```json
{
  "query": "anticipatory bail",
  "objective": "summarize",
  "selected": [
    {
      "id": "src-1",
      "title": "Example Source",
      "url": "https://example.org/doc",
      "snippet": "Key source snippet"
    }
  ]
}
```

### `POST /api/v1/knowledge-base/provision-lookup`
Retrieves relevant legal provisions and optionally starts async analysis.

**Request body**
```json
{
  "query": "cheque bounce",
  "facts": "notice sent, payment not made",
  "limit": 8,
  "startAnalysis": true
}
```

### `GET /api/v1/knowledge-base/provision-lookup/analysis/{job_id}`
Checks async analysis status (`ready | pending | error | not_found`).

### `POST /api/v1/knowledge-base/provision-cache/clear`
Clears provision-result cache.

---

## 3) Agent endpoints

All agent endpoints are `POST` and accept flexible JSON payloads unless noted.

| Endpoint | Prompt task | Response shape |
|---|---|---|
| `/api/v1/agents/issue-spotter` | `issue_spotter` | `issues[]` |
| `/api/v1/agents/case-finder` | `case_finder` | `precedents[]` |
| `/api/v1/agents/limitation-checker` | `limitation_checker` | `assessment` object |
| `/api/v1/agents/argument-builder` | `argument_builder` | `argumentSet` object |
| `/api/v1/agents/doc-composer` | `doc_composer` | `draft` object |
| `/api/v1/agents/compliance-guard` | `compliance_guard` | `findings[]` |
| `/api/v1/agents/aid-connector` | `aid_connector` | `aid` object |
| `/api/v1/agents/judgment-summarizer` | `judgment_summarizer` | `summary` object |

### `POST /api/v1/agents/judgment-summarizer` (multipart)
This endpoint expects file upload data.

**Form-data**
- `file` (required): PDF, DOCX, or TXT containing judgment text.

---

## 4) cURL quick examples

```bash
# Health
curl http://localhost:8000/api/v1/health

# Issue Spotter
curl -X POST http://localhost:8000/api/v1/agents/issue-spotter \
  -H "Content-Type: application/json" \
  -d @backend/sample-issue-input.json

# Live Search
curl -X POST http://localhost:8000/api/v1/knowledge-base/live-search \
  -H "Content-Type: application/json" \
  -d '{"query":"bail","intent":"case_law","limit":5}'

# Judgment Summarizer (multipart upload)
curl -X POST http://localhost:8000/api/v1/agents/judgment-summarizer \
  -F "file=@/path/to/judgment.pdf"
```

---

## 5) Notes for integrators

- Some responses are dynamically shaped by LLM output; always code defensively.
- For long-running provision analysis, call `provision-lookup` first and poll the analysis status endpoint.
- If the knowledge service or provider key is unavailable, the API returns 503 with structured error payload.
