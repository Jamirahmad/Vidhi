# Ingestion Strategy (Vidhi Legal Intelligence Platform)

## 1. Overview

The ingestion layer is the **foundation of Vidhi**. It is responsible for collecting, validating, cleaning, normalizing, and storing legal documents from multiple authoritative sources such as:

- Supreme Court of India
- High Courts
- Tribunals (NCLT, ITAT, CAT, NGT, etc.)
- India Code (Acts, Rules, Amendments)
- Gazette notifications
- User uploaded case documents
- Public legal datasets (data.gov.in)
- Secondary sources (Indian Kanoon as fallback/index)

The ingestion pipeline must ensure:

- **High accuracy**
- **Traceability of citations**
- **Scalable processing**
- **Strict compliance & auditability**
- **Support for multiple document formats**

---

## 2. Core Ingestion Goals

### 2.1 Accuracy and Legal Trustworthiness
Vidhi must prioritize official sources to prevent misinformation.

### 2.2 Source Traceability
Every ingested document must contain:

- `source_url`
- `download_timestamp`
- `court_or_body`
- `document_hash`
- `document_version`

This ensures Vidhi can always explain **where the information came from**.

### 2.3 Format Standardization
Legal data arrives in many forms:

- HTML case pages
- PDF judgments
- scanned PDFs
- gazette notifications
- user uploaded Word/PDF documents

All must be normalized into a unified internal representation.

### 2.4 Scalable Storage and Retrieval
Ingestion must support:

- batch ingestion (daily/weekly jobs)
- near real-time ingestion (alerts / new judgments)
- incremental refresh

---

## 3. Ingestion Architecture (High-Level)

Vidhi ingestion is designed as a **multi-stage pipeline**:

1. **Source Discovery**
2. **Fetching / Download**
3. **Parsing**
4. **OCR (if needed)**
5. **Cleaning and Normalization**
6. **Metadata Extraction**
7. **Chunking**
8. **Embedding + Vector Store**
9. **Indexing and Search**
10. **Audit Logging**
11. **Storage in Data Lake**

---

## 4. Ingestion Modes

Vidhi supports multiple ingestion modes depending on the source type.

---

### 4.1 Scheduled Batch Ingestion (Primary Mode)

Used for:
- Supreme Court judgments
- High Court judgments
- tribunal orders
- gazette notifications

Runs:
- Daily or weekly
- configurable per source

Advantages:
- stable ingestion
- avoids rate-limit issues
- predictable performance

---

### 4.2 Event Driven Ingestion (Optional / Enhancement)

Used for:
- newly published orders
- compliance alerts
- new gazette notifications

Triggered by:
- RSS feeds
- notifications
- polling endpoints

---

### 4.3 User Upload Ingestion (Interactive Mode)

Used when a user uploads:

- case documents
- contracts
- FIR / charge sheets
- affidavits

Runs:
- on demand
- per user session

This ingestion must enforce **security, encryption, and retention policies**.

---

## 5. Source-Specific Ingestion Strategy

Vidhi uses a **source adapter pattern**, where each source has its own extractor.

---

### 5.1 Supreme Court of India (SCI)

**Preferred Data Type**
- PDF judgments
- daily orders

**Challenges**
- scanned PDFs
- inconsistent metadata
- varying formatting across years

**Strategy**
- scrape judgment listing pages
- download PDF
- compute SHA256 hash
- extract metadata
- store in raw + processed zones

---

### 5.2 High Courts

**Preferred Data Type**
- PDF judgments + HTML metadata

**Challenges**
- different HTML layouts across courts
- rate limits
- unstable portals

**Strategy**
- build one adapter per HC portal
- implement retry, caching, and backoff
- maintain court-wise parsing rules

---

### 5.3 Tribunals (NCLT, ITAT, CAT, NGT, CESTAT)

**Challenges**
- tribunal portals have inconsistent search pages
- PDFs often scanned

**Strategy**
- use tribunal-specific crawlers
- OCR fallback enabled by default
- metadata tagging for tribunal bench/location

---

### 5.4 India Code (Acts/Rules)

**Data Type**
- HTML structured Acts
- linked PDFs

**Strategy**
- parse structured HTML into clean statute sections
- store section-wise breakdown
- build "Act Graph" linking:
  - Act → Sections → Amendments → Notifications

---

### 5.5 Gazette of India

**Data Type**
- PDF notifications

**Challenges**
- scanned documents
- large file sizes

**Strategy**
- keyword-based indexing (Ministry, Act, Subject)
- OCR required frequently
- maintain date-based partitions

---

### 5.6 Indian Kanoon (Secondary Index Source)

**Purpose**
- fast discovery of judgments
- citation linking
- fallback when official site fails

**Strategy**
- use only for indexing metadata and references
- avoid treating as authoritative if official copy exists
- store a `trust_score` for each document

---

### 5.7 User Uploaded Documents

**Challenges**
- personal data
- confidentiality
- inconsistent formatting

**Strategy**
- extract text + metadata
- mask sensitive data (optional)
- encrypt at rest
- delete after retention period

---

## 6. Data Pipeline Stages (Detailed)

---

### 6.1 Stage 1: Source Discovery

Discovery identifies which documents are new.

**Methods**
- scrape listing pages
- pagination crawl
- date-based queries
- case-number-based query
- incremental ingestion using last checkpoint

**Output**
- list of `document_candidates`

---

### 6.2 Stage 2: Fetching and Download

Responsible for downloading the actual document.

**Key Rules**
- rate limit per domain
- exponential backoff
- store original file in raw storage

**Output**
- `raw_pdf` / `raw_html`
- `download_status`

---

### 6.3 Stage 3: Validation & Integrity Check

Ensures file is valid.

Validation includes:
- file not empty
- PDF is readable
- HTML not blocked by captcha
- checksum match (optional)

**Output**
- `document_hash`
- validation status

---

### 6.4 Stage 4: Parsing and Text Extraction

If source is HTML:
- use DOM parsing (BeautifulSoup / lxml)

If source is PDF:
- use PDF text extraction tools
- detect if scanned (no embedded text)

**Output**
- `raw_text`
- `raw_metadata`

---

### 6.5 Stage 5: OCR (Scanned PDF Handling)

OCR is applied only when:
- PDF has no text layer
- extracted text is below threshold

**OCR Tools**
- Tesseract OCR (default)
- AWS Textract (future enhancement)

**Output**
- `ocr_text`

---

### 6.6 Stage 6: Cleaning and Normalization

Cleaning ensures consistent text.

Cleaning rules:
- remove headers/footers repeated per page
- normalize whitespace
- normalize unicode characters
- remove page numbers
- detect and remove watermark text
- preserve legal formatting (sections, headings)

**Output**
- `clean_text`

---

### 6.7 Stage 7: Metadata Extraction

Metadata is extracted from:
- court header text
- PDF first page
- HTML case fields

**Metadata Fields**
- court name
- bench / judges
- case number
- parties
- advocates (if available)
- date of judgment
- act references
- citations (SCC/AIR/ALLMR/CRLJ)

**Output**
- `metadata.json`

---

### 6.8 Stage 8: Legal Structure Extraction

This stage enriches the document.

Extract:
- case summary (if present)
- issues
- arguments
- findings
- final order / judgment
- referenced judgments
- referenced acts/sections

This stage powers:
- citation graphs
- legal reasoning chains
- precedent linking

---

### 6.9 Stage 9: Chunking Strategy

Vidhi uses a **semantic + structural chunking approach**.

Chunk boundaries should align with:

- headings (Facts, Arguments, Findings)
- numbered paragraphs
- section headers (Act Section references)

Chunk size rules:
- 600 to 1200 tokens per chunk (configurable)
- overlap: 80 to 120 tokens
- preserve paragraph numbering

**Output**
- `chunked_text.jsonl`

---

### 6.10 Stage 10: Embedding Generation

Each chunk is embedded and stored for semantic retrieval.

Embedding inputs include:
- chunk text
- metadata tags (court, year, act)

Embedding output:
- `vector_embedding`
- `chunk_id`

---

### 6.11 Stage 11: Indexing in Vector Store

Supported stores:
- FAISS (local optimized)
- ChromaDB (metadata filtering)

Index keys:
- `doc_id`
- `chunk_id`
- `court`
- `year`
- `act_reference`
- `trust_score`

---

### 6.12 Stage 12: Audit Logging and Observability

Every ingestion run must generate logs:

- ingestion start/end time
- documents processed
- documents failed
- OCR usage count
- extraction accuracy signals
- warnings for missing metadata

Outputs:
- ingestion logs in JSON
- pipeline metrics for dashboards

---

## 7. Data Storage Strategy (Lakehouse Design)

Vidhi uses a layered storage model.

---

### 7.1 Raw Zone

Stores:
- original PDFs
- original HTML
- source snapshots

Path example:
- `data/raw/sci/2026/01/`
- `data/raw/hc/bombay/2025/`

---

### 7.2 Processed Zone

Stores:
- extracted text
- cleaned normalized text
- metadata json

Path example:
- `data/processed/judgments/`
- `data/processed/statutes/`

---

### 7.3 Curated Zone

Stores:
- chunked content
- structured legal entities
- citation graphs
- act mappings

Path example:
- `data/curated/chunks/`
- `data/curated/act_graph/`

---

### 7.4 Vector Zone

Stores:
- embeddings
- FAISS/Chroma indices

Path example:
- `vectorstore/faiss/`
- `vectorstore/chroma/`

---

## 8. Document ID and Versioning

Every document must have a stable identifier:

### 8.1 Doc ID Format

Recommended:
```yaml
DOC-{SOURCE}-{COURT}-{YEAR}-{CASE_NUMBER_HASH}

Example:
DOC-SCI-SUPREMECOURT-2024-7B29A3
```

---

### 8.2 Versioning

If the same case is re-downloaded:
- compare hashes
- store as new version only if content changes

Fields:
- `doc_version`
- `doc_hash`
- `previous_hash`

---

## 9. Trust Scoring (Source Credibility Ranking)

Vidhi assigns a trust score to every document.

Example trust scale:
- 1.0 = official court portal PDF
- 0.8 = tribunal portal PDF
- 0.6 = Indian Kanoon
- 0.4 = news portal summary
- 0.3 = unknown blog reference

Trust score influences:
- retrieval ranking
- citation selection
- response confidence

---

## 10. Error Handling Strategy

Failures are expected in ingestion.

### 10.1 Retry Policies

- 3 retries per URL
- exponential backoff
- circuit breaker for repeated failures

### 10.2 Failure Classification

- Network timeout
- Captcha blocked
- PDF corrupted
- OCR failure
- Metadata extraction failure

Each failure must be logged with:
- reason code
- source URL
- timestamp
- stack trace (internal only)

---

## 11. Security & Compliance Considerations

### 11.1 Data Privacy

User-uploaded documents may contain:
- Aadhaar numbers
- phone numbers
- addresses
- bank account details

Vidhi must support:
- encryption at rest
- masking and redaction
- controlled access policies

---

### 11.2 Retention Policy

Recommended:
- raw scraped court documents: retain indefinitely
- user uploads: configurable retention (default 30 days)
- audit logs: retain for 180 days minimum

---

### 11.3 Legal and Ethical Boundaries

- Respect robots.txt (where applicable)
- Avoid scraping paid sources without authorization
- Always store original source references
- Do not modify the meaning of legal text

---

## 12. Performance Optimization Strategy

To scale ingestion:

### 12.1 Parallelism

- multi-threaded download pool
- separate workers for OCR tasks

### 12.2 Caching

- store visited URLs
- store last ingestion checkpoints per source

### 12.3 Incremental Updates

Use `last_seen_date` and `last_doc_id` checkpoint.

---

## 13. Monitoring and Metrics

Key ingestion KPIs:

- documents ingested per run
- success rate %
- OCR usage %
- average processing time per doc
- metadata completeness %
- duplicates detected %
- court-wise failure rate

These metrics will feed the **IngestionOps Dashboard**.

---

## 14. Quality Assurance Strategy

To ensure ingestion correctness:

### 14.1 Sampling Validation

Randomly validate:
- 5% of newly ingested documents daily

Validation includes:
- metadata correctness
- case number match
- date extraction accuracy
- citation extraction accuracy

---

### 14.2 Regression Testing

Maintain a test suite of:
- known judgments
- known gazette notifications
- known statute sections

Each ingestion update must re-run tests.

---

## 15. Output Artifacts Produced

For every ingested document, Vidhi generates:

- raw document file (PDF/HTML)
- extracted raw text
- OCR corrected text (if needed)
- cleaned normalized text
- metadata JSON
- chunk JSONL
- embeddings
- index references
- ingestion logs

---

## 16. Future Enhancements

### 16.1 Textract Integration
Replace OCR with AWS Textract for better accuracy.

### 16.2 Multi-Language Support
Support for regional judgments in:
- Hindi
- Marathi
- Tamil
- Kannada
- Bengali

### 16.3 Citation Graph Builder
Automatically build precedent networks.

### 16.4 Differential Updates
Detect and ingest only changed pages using hashing.

---

## 17. Summary

Vidhi ingestion is designed to be:

- modular (adapter-driven)
- scalable (batch + event-driven)
- accurate (metadata + trust scoring)
- legally reliable (source traceability)
- retrieval-ready (chunking + embeddings)

This ingestion strategy ensures Vidhi can build a trustworthy legal knowledge base
capable of powering AI-based legal research, drafting, and compliance reasoning.

---
