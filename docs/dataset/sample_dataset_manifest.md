# Sample Dataset Manifest — Vidhi

This document defines the **sample dataset manifest format** for Vidhi.  
It helps track what data has been ingested, where it came from, its legal source, processing status, and whether it is safe to use for evaluation or demos.

This is especially useful for:
- auditing ingestion
- verifying citation reliability
- ensuring legal/ethical data sourcing
- tracking dataset completeness
- debugging missing case metadata

---

## Purpose

The **Sample Dataset Manifest** is a lightweight registry of documents ingested into Vidhi’s pipeline.  
It records:

- Data source (Supreme Court / High Court / Tribunal / Gazette / Manual Upload)
- Document type (Judgment / Order / Act / Notification)
- Format (PDF / HTML / DOCX)
- Processing state (raw → cleaned → chunked → embedded)
- Storage references (local paths + vectorstore IDs)
- Citation reliability score

---

## Recommended File Location

Store this file at:
```yaml
docs/dataset/sample_dataset_manifest.md
```

---

## Manifest Structure

Each dataset entry should contain:

- **Document ID**: unique identifier
- **Source Court / Authority**
- **Document Title**
- **Citation Reference**
- **URL**
- **Document Type**
- **File Format**
- **Language**
- **Jurisdiction**
- **Date of Judgment / Publication**
- **Ingestion Date**
- **Processing Status**
- **Vectorstore Status**
- **Metadata Completeness**
- **Legal Use Notes**
- **Validation Notes**

---

## Sample Dataset Entries

### 1) Supreme Court Judgment

| Field | Value |
|------|-------|
| Document ID | SC_2020_001 |
| Source Authority | Supreme Court of India |
| Title | Example Criminal Appeal Judgment |
| Citation | (2020) SC Example Citation |
| Official URL | https://main.sci.gov.in/ |
| Document Type | Judgment |
| Format | PDF |
| Language | English |
| Jurisdiction | India |
| Judgment Date | 2020-08-14 |
| Ingestion Date | 2026-01-10 |
| Pipeline Stage | Chunked + Embedded |
| Storage Path | `data/raw/sc/SC_2020_001.pdf` |
| Clean Text Path | `data/processed/cleaned_text/SC_2020_001.txt` |
| Chunk Metadata | `data/chunks/chunk_metadata/SC_2020_001.json` |
| Vectorstore Index | ChromaDB |
| Vectorstore Document IDs | `sc_2020_001_chunk_1 ... chunk_n` |
| Metadata Completeness | High |
| Citation Reliability | High |
| Notes | Verified citation format and court source |

---

### 2) High Court Judgment

| Field | Value |
|------|-------|
| Document ID | HC_BOM_2021_002 |
| Source Authority | Bombay High Court |
| Title | Example Bail Order |
| Citation | 2021 Bom HC Example |
| Official URL | https://bombayhighcourt.nic.in/ |
| Document Type | Order |
| Format | PDF |
| Language | English |
| Jurisdiction | Maharashtra |
| Judgment Date | 2021-03-21 |
| Ingestion Date | 2026-01-11 |
| Pipeline Stage | Cleaned + Chunked |
| Storage Path | `data/raw/hc/HC_BOM_2021_002.pdf` |
| Clean Text Path | `data/processed/cleaned_text/HC_BOM_2021_002.txt` |
| Chunk Metadata | `data/chunks/chunk_metadata/HC_BOM_2021_002.json` |
| Vectorstore Index | FAISS |
| Vectorstore Document IDs | `hc_bom_2021_002_chunk_1 ... chunk_n` |
| Metadata Completeness | Medium |
| Citation Reliability | Medium |
| Notes | Citation formatting differs across HC documents |

---

### 3) Tribunal Case Document

| Field | Value |
|------|-------|
| Document ID | NCLT_2022_003 |
| Source Authority | NCLT |
| Title | Example Insolvency Resolution Order |
| Citation | NCLT Order Ref No. XYZ |
| Official URL | https://nclt.gov.in/ |
| Document Type | Order |
| Format | PDF |
| Language | English |
| Jurisdiction | India |
| Judgment Date | 2022-07-09 |
| Ingestion Date | 2026-01-12 |
| Pipeline Stage | Raw Only |
| Storage Path | `data/raw/tribunals/NCLT_2022_003.pdf` |
| Clean Text Path | Pending |
| Chunk Metadata | Pending |
| Vectorstore Index | Not Embedded |
| Metadata Completeness | Low |
| Citation Reliability | Low |
| Notes | OCR required due to scanned PDF |

---

### 4) Gazette / Statutory Notification

| Field | Value |
|------|-------|
| Document ID | GAZ_2019_004 |
| Source Authority | Gazette of India |
| Title | Example Amendment Notification |
| Citation | Gazette Notification No. ABC |
| Official URL | https://egazette.nic.in/ |
| Document Type | Notification |
| Format | PDF |
| Language | English |
| Jurisdiction | India |
| Publication Date | 2019-12-18 |
| Ingestion Date | 2026-01-15 |
| Pipeline Stage | Embedded |
| Storage Path | `data/raw/statutes/GAZ_2019_004.pdf` |
| Clean Text Path | `data/processed/cleaned_text/GAZ_2019_004.txt` |
| Chunk Metadata | `data/chunks/chunk_metadata/GAZ_2019_004.json` |
| Vectorstore Index | ChromaDB |
| Metadata Completeness | High |
| Citation Reliability | High |
| Notes | Used for statute reference validation |

---

### 5) User Uploaded Document (Manual Input)

| Field | Value |
|------|-------|
| Document ID | USER_UPLOAD_0001 |
| Source Authority | User Provided |
| Title | Client Agreement (Sample Draft) |
| Citation | N/A |
| URL | N/A |
| Document Type | Uploaded Draft |
| Format | DOCX |
| Language | English |
| Jurisdiction | Maharashtra |
| Upload Date | 2026-01-20 |
| Pipeline Stage | Parsed + Cleaned |
| Storage Path | `data/raw/user_uploads/USER_UPLOAD_0001.docx` |
| Clean Text Path | `data/processed/cleaned_text/USER_UPLOAD_0001.txt` |
| Chunk Metadata | `data/chunks/chunk_metadata/USER_UPLOAD_0001.json` |
| Vectorstore Index | Local FAISS |
| Metadata Completeness | Medium |
| Citation Reliability | Not Applicable |
| Notes | Treated as private user document, excluded from shared evaluation |

---

## Dataset Summary Table

| Dataset Type | Count | Source Examples | Status |
|-------------|-------|----------------|--------|
| Supreme Court Judgments | 10 | SCI Portal | Embedded |
| High Court Judgments | 20 | HC Websites | Embedded |
| Tribunal Orders | 15 | NCLT / NCDRC | Partial OCR |
| Statutes / Gazette | 5 | Gazette of India | Embedded |
| User Uploads | 5 | Manual Intake | Not Shared |

---

## Processing Status Definitions

| Stage | Meaning |
|------|---------|
| Raw | Document downloaded/uploaded but not parsed |
| Parsed | Extracted text from PDF/HTML/DOCX |
| Cleaned | Removed headers/footers, normalized spacing |
| Chunked | Split into retrieval-friendly chunks |
| Embedded | Stored in vectorstore with embeddings |
| Validated | Citation + metadata verified |
| Production Ready | Suitable for research & drafting workflows |

---

## Citation Reliability Levels

| Level | Meaning |
|------|---------|
| High | Direct court website / official gazette source |
| Medium | Public portal but formatting inconsistent |
| Low | OCR-based or scraped text with missing metadata |
| Unknown | User-uploaded or unverifiable source |

---

## Legal and Ethical Notes

- Only ingest sources that are publicly available or legally accessible.
- Avoid publishing copyrighted legal databases unless explicitly permitted.
- Ensure that personal details (PII) are masked if documents contain sensitive data.
- Always store raw sources for audit traceability.

---

## Future Enhancements

- Add checksum validation (SHA256) per file
- Add automated metadata extraction accuracy score
- Add "citation verified" boolean field
- Integrate manifest generation into ingestion pipeline

---
