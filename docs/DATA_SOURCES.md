## 1. Objective

Vidhi requires access to reliable legal documents to support:

- case law research (precedent discovery)
- extraction of legal principles and judicial reasoning
- citation-backed drafting of petitions, notices, and applications
- jurisdiction-aware filtering (SC vs HC vs Tribunals)
- legal compliance checks (formatting + annexures + filing requirements)

The system should prioritize **accuracy**, **traceability**, and **public availability** of judgments.

---

## 2. Data Source Categories

Vidhi supports ingestion from three major categories:

### A) Official Court Websites (Preferred)
These are the most authoritative sources of judgments.

### B) Tribunal Websites
Tribunal portals often provide judgments in PDF/HTML formats.

### C) Public Legal Repositories (Optional / Community-Based)
These sources can accelerate research but must be used carefully.

---

## 3. Supreme Court of India (SC)

### Primary Source
- Supreme Court of India official website:
  - Judgment archives
  - Daily orders
  - Cause lists (optional metadata)

### Types of documents
- Final Judgments
- Interim Orders
- Review/Curative petitions (limited)
- Constitutional bench rulings

### Common Formats
- PDF
- HTML (occasionally)

### Ingestion Notes
- SC judgments are usually well-structured.
- Citation patterns are consistent (SCC, AIR, SCR).
- Most SC judgments are high-value due to nationwide applicability.

### Recommended Ingestion Priority
- Landmark criminal bail judgments (CrPC 437/439)
- economic offense and fraud cases (IPC 420/467/468/471)
- constitutional rights (Article 14, 19, 21)
- civil procedure interpretations (CPC, limitation act)

---

## 4. High Courts (HC)

India has 25 High Courts, and each has its own portal and judgment database format.

### Primary Sources
- Bombay High Court
- Delhi High Court
- Karnataka High Court
- Madras High Court
- Calcutta High Court
- Allahabad High Court
- Gujarat High Court
- Telangana High Court
- Punjab & Haryana High Court
- Kerala High Court
- Rajasthan High Court
- Madhya Pradesh High Court
- Patna High Court
- Jharkhand High Court
- Orissa High Court
- Chhattisgarh High Court
- Uttarakhand High Court
- Himachal Pradesh High Court
- Jammu & Kashmir and Ladakh High Court
- Manipur High Court
- Meghalaya High Court
- Tripura High Court
- Sikkim High Court
- Gauhati High Court

### Common Formats
- PDF judgments
- scanned documents (OCR required)
- HTML pages with embedded PDFs

### Ingestion Notes
- HC judgments are critical for **jurisdiction-specific precedent**.
- Metadata can be inconsistent (case numbers, dates, bench details).
- Many portals block scraping unless rate-limited.

### Recommended Ingestion Priority (Capstone Scope)
For demonstration, focus on 3–5 high-volume courts:
- Supreme Court (SC)
- Bombay High Court (Maharashtra)
- Delhi High Court
- Karnataka High Court
- Madras High Court

This provides strong coverage while keeping ingestion manageable.

---

## 5. Tribunals (Specialized Courts)

Tribunals are essential for corporate, tax, service, and consumer matters.

### Major Tribunal Sources

#### A) NCLT / NCLAT (Company Law)
- Insolvency and Bankruptcy Code (IBC)
- Corporate restructuring cases

#### B) ITAT (Income Tax Appellate Tribunal)
- tax appeals and assessment disputes

#### C) CAT (Central Administrative Tribunal)
- government service disputes

#### D) Consumer Forums
- District / State Consumer Disputes Redressal Commissions
- National Consumer Disputes Redressal Commission (NCDRC)

#### E) DRAT / DRT
- debt recovery and banking disputes

#### F) SAT (Securities Appellate Tribunal)
- SEBI-related cases

### Formats
- PDF
- HTML (occasionally)
- scanned images

### Ingestion Notes
- tribunal judgments often have limited citation structure.
- OCR quality becomes critical for older judgments.
- classification by domain is easier because tribunal focus is narrow.

---

## 6. Statutes & Bare Acts Sources

Vidhi should support retrieval of statutory provisions, not only judgments.

### Recommended Sources
- India Code portal (official bare acts)
- Gazette publications (optional)
- public government legislative portals

### Examples
- IPC
- CrPC
- CPC
- Indian Evidence Act
- Limitation Act
- Negotiable Instruments Act
- Companies Act
- IBC
- Consumer Protection Act
- Special Acts (state or central)

### Ingestion Notes
- Acts should be stored as structured sections.
- Acts should be chunked by section for accurate retrieval.

---

## 7. Optional Sources (Use Carefully)

These sources can be helpful for fast research but may introduce risks:

### A) Indian Kanoon
- Large searchable database
- Highly useful for quick discovery
- Must respect licensing and ToS restrictions

### B) Open Legal Archives / University Collections
- sometimes provide curated datasets

### C) Government / Departmental websites
- circulars, notifications, policy documents

### Usage Recommendation
For capstone:
- use only a small subset of documents
- store citations and URLs for traceability
- avoid bulk redistribution

---

## 8. Ingestion Strategy Overview

Vidhi ingestion follows a staged approach:

### Stage 1 — Identify Sources & Access Mode
Each source is categorized as:

- Direct download (PDF link)
- HTML page parsing
- OCR-required scanned PDFs
- manual upload (user)

### Stage 2 — Fetch & Store Raw Files
Store all raw files under:

```
data/raw/sc/
data/raw/hc/
data/raw/tribunals/
data/raw/user_uploads/
```

### Stage 3 — Parse & Extract Text
Use parsing modules:

- PDF parsing (text-based PDFs)
- HTML parsing
- OCR parsing for scanned documents

### Stage 4 — Clean and Normalize
Cleaning steps include:

- removing headers/footers
- removing page numbers
- standardizing whitespace
- removing duplicated content
- fixing encoding issues

### Stage 5 — Metadata Extraction
Extract:

- court name
- bench/judge
- judgment date
- case number
- parties involved
- citations
- legal sections mentioned

### Stage 6 — Chunking
Chunking is performed with overlap to preserve legal context:

- chunk size: 500–1200 tokens
- overlap: 100–200 tokens

### Stage 7 — Embeddings + Vector Store Build
Each chunk is embedded and stored in:

- FAISS (fast local)
- ChromaDB (persistent and filter-friendly)

Stored at:

```
vectorstore/faiss_index/
vectorstore/chroma_db/
```

---

## 9. Recommended Ingestion Strategy for Capstone Demo

Full ingestion of all Indian judgments is unrealistic.  
So Vidhi should follow a **progressive dataset strategy**:

### Step 1: Start with a focused legal domain
For example:
- bail cases (CrPC 437/439)
- economic offenses (IPC 420, 467, 468, 471)
- property disputes and limitation issues

### Step 2: Collect 50–200 judgments for demo
This is sufficient to demonstrate:
- similarity search
- citations
- contradiction detection
- drafting workflows

### Step 3: Expand gradually
After demo success:
- scale to 1000+ judgments
- add tribunal-specific datasets
- add bare acts for statutory retrieval

---

## 10. Data Validation & Quality Checks

Legal outputs must be traceable. Therefore:

### Mandatory checks
- every stored chunk must have a `source_doc_id`
- every doc must have `court` + `date`
- citations must be extracted where possible
- OCR documents must be flagged as OCR-based (lower confidence)

### Citation validation
Vidhi uses:

- `src/core/citation_validator.py`
- `src/evaluation/citation_accuracy_tests.py`

The drafting agent must cite retrieved sources.

---

## 11. Compliance and Safety Considerations

Vidhi is a research assistant, not a legal authority.

Therefore:

- do not fabricate citations
- do not hallucinate case names
- do not generate binding legal advice
- always ask for lawyer verification before filing

Also ensure:
- rate limiting in scrapers
- compliance with website ToS
- use public domain / publicly accessible documents for demo

---

## 12. Storage Strategy (Local + Cloud)

### Local Development
- store dataset in `data/`
- persist vectorstore locally

### AWS Free Tier Strategy
- store raw judgments in S3 (optional)
- persist vectorstore on EC2 disk or EBS
- rebuild index incrementally

### Streamlit Cloud Strategy
- do not ingest dynamically
- use prebuilt sample vectorstore
- restrict dataset size

---

## 13. Mapping Sources to Repository Modules

| Category | Module Location |
|---------|-----------------|
| Supreme Court scraping | `src/ingestion/fetchers/sc_scraper.py` |
| High Court scraping | `src/ingestion/fetchers/hc_scraper.py` |
| Tribunal scraping | `src/ingestion/fetchers/tribunal_scraper.py` |
| Indian Kanoon connector | `src/ingestion/fetchers/indian_kanoon_connector.py` |
| PDF parsing | `src/ingestion/parsers/pdf_parser.py` |
| HTML parsing | `src/ingestion/parsers/html_parser.py` |
| OCR parsing | `src/ingestion/parsers/ocr_parser.py` |
| Text cleaning | `src/ingestion/cleaners/text_cleaner.py` |
| Chunking | `src/ingestion/chunking/chunker.py` |
| Metadata extraction | `src/ingestion/metadata/metadata_extractor.py` |
| Ingestion pipeline runner | `src/ingestion/pipelines/ingestion_runner.py` |
| Vector store build | `src/retrieval/vector_store_manager.py` |

---

## 14. Recommended Dataset Manifest Format

Vidhi maintains a dataset manifest file for traceability.

Example manifest entry:

```json
{
  "doc_id": "SC_2012_000123",
  "source": "Supreme Court Website",
  "court": "Supreme Court of India",
  "case_title": "Sanjay Chandra v. CBI",
  "citation": "(2012) 1 SCC 40",
  "judgment_date": "2012-02-15",
  "download_url": "https://...",
  "format": "pdf",
  "language": "en",
  "ingested_on": "2026-02-01",
  "checksum": "sha256:..."
}
```

---

## 15. Summary

Vidhi’s ingestion strategy is designed to:

- prioritize authoritative sources
- maintain metadata consistency
- support multilingual documents
- enable citation-backed drafting
- remain free-tier friendly for capstone demo

This ensures that the retrieval engine and drafting workflow are grounded in real judgments and statutory provisions.

---

## Related Documents

- `docs/DATA_INGESTION.md`
- `docs/DEPLOYMENT.md`
- `docs/dataset/ingestion_strategy.md`
- `docs/dataset/data_sources.md`
- `docs/architecture/data_ingestion_pipeline.png`
- `docs/architecture/deployment_free_tier.png`

