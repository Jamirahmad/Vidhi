# Data Sources for Vidhi (Indian Legal Ecosystem)

## Overview

Vidhi requires **high-quality, authoritative, and legally usable sources** to ensure that legal research and document drafting outputs are **accurate, verifiable, and citation-backed**.

This document lists all potential legal data sources, categorized by:

- **Court type (Supreme Court / High Courts / Tribunals)**
- **Statutes and legislation**
- **Case law repositories**
- **Government gazettes**
- **Legal databases**
- **Open datasets**
- **User-uploaded documents**
- **Secondary references (commentary, journals, digests)**

For each source, we identify:
- **Source Type** (Website / Database / PDF / HTML / API / Bulk Dataset)
- **Access Method** (Scraping / Public API / Manual download / User upload)
- **Expected Output** (PDF orders, judgments, citations, metadata)

---

## 1. Primary Judicial Sources (Most Reliable)

These are **official court-owned sources**, preferred for production-grade ingestion.

---

### 1.1 Supreme Court of India (SCI)

**Source**
- [Supreme Court of India Official Website](https://www.sci.gov.in/)

**Source Type**
- Website (HTML + PDF Judgments)
- Cause lists, orders, daily judgments

**Content Available**
- Judgments
- Orders
- Case status
- Bench details
- Party details
- Date of hearing
- Citation references

**Ingestion Method**
- Web scraping (HTML + PDF downloads)
- Metadata extraction
- OCR support for scanned PDFs

---

### 1.2 High Courts (HC)

**Source**
- [eCourts High Court Portals](https://ecourts.gov.in/)

- Individual High Court websites (examples):
  - [Bombay High Court](https://bombayhighcourt.nic.in/)
  - [Delhi High Court](https://delhihighcourt.nic.in/)
  - [Madras High Court](https://www.hcmadras.tn.nic.in/)
  - [Karnataka High Court](https://karnatakajudiciary.kar.nic.in/)

**Source Type**
- Websites (HTML + PDF)
- Court-specific databases

**Content Available**
- Case status
- Judgments and orders
- Cause lists
- Daily board updates
- Case filing numbers and parties

**Ingestion Method**
- Court-specific scrapers (per HC portal structure)
- PDF ingestion + metadata extraction
- Retry and rate limiting (portals can be slow/unreliable)

---

### 1.3 District Courts via eCourts

**Source**
- [eCourts Services Portal](https://services.ecourts.gov.in/)

**Source Type**
- Website database
- Court case status and orders

**Content Available**
- Case proceedings summary
- Hearing dates
- Orders uploaded by court registry

**Ingestion Method**
- Scraper + case-id driven fetch
- Structured metadata extraction

---

## 2. Tribunals & Specialized Courts

Tribunals are extremely important in India because large litigation volume happens outside traditional courts.

---

### 2.1 National Company Law Tribunal (NCLT)

**Source**
- [NCLT Official Portal](https://nclt.gov.in/)

**Source Type**
- Website + PDF orders

**Content Available**
- Corporate insolvency cases
- Company disputes
- Tribunal orders and judgments

**Ingestion Method**
- Scrape order listings
- Download PDFs
- Extract bench + date + case number metadata

---

### 2.2 National Company Law Appellate Tribunal (NCLAT)

**Source**
- [NCLAT Official Portal](https://nclat.nic.in/)

**Source Type**
- Website + PDF judgments

---

### 2.3 Central Administrative Tribunal (CAT)

**Source**
- [CAT Official Portal](https://cgat.gov.in/)

**Source Type**
- Website + PDF orders

**Key Domain**
- Service matters (Govt employees)

---

### 2.4 Income Tax Appellate Tribunal (ITAT)

**Source**
- [ITAT Portal](https://itat.gov.in/)

**Source Type**
- Website + PDF judgments

**Key Domain**
- Income tax disputes

---

### 2.5 Customs, Excise & Service Tax Appellate Tribunal (CESTAT)

**Source**
- [CESTAT Portal](https://cestat.gov.in/)

**Source Type**
- Website + PDF orders

---

### 2.6 National Green Tribunal (NGT)

**Source**
- [NGT Portal](https://greentribunal.gov.in/)

**Source Type**
- Website + PDF judgments

**Key Domain**
- Environmental cases

---

### 2.7 Consumer Disputes Redressal Commissions

**Sources**
- [National Commission (NCDRC)](https://ncdrc.nic.in/)

- State Commissions (varies by state)

**Source Type**
- Website + PDF orders

**Key Domain**
- Consumer protection cases

---

### 2.8 Armed Forces Tribunal (AFT)

**Source**
- [AFT Portal](https://aftdelhi.nic.in/)

**Source Type**
- Website + PDF judgments

---

## 3. Statutes, Rules, Acts & Regulations (Legislation Sources)

Statutes are critical for IssueSpotter and ComplianceGuard agents.

---

### 3.1 India Code (Official Government Statute Repository)

**Source**
- [India Code Portal (Legislative Department, GoI)](https://www.indiacode.nic.in/)

**Source Type**
- Government database website
- HTML + PDF Acts

**Content Available**
- Central Acts
- Rules
- Amendments
- Notifications linked to Acts

**Ingestion Method**
- HTML ingestion for structured parsing
- PDF download for official archival references

---

### 3.2 Gazette of India

**Source**
- [eGazette Portal](https://egazette.nic.in/)

**Source Type**
- Official Government PDF notifications

**Content Available**
- New acts, amendments, rules, notifications
- Ministry circulars

**Ingestion Method**
- Keyword-based scraping
- Document download + OCR

---

### 3.3 Ministry Websites (Rules, Notifications, Circulars)

Some regulations are only accessible through ministry portals.

Examples:
- [Ministry of Corporate Affairs (MCA)](https://www.mca.gov.in/)
- [Ministry of Finance](https://finmin.gov.in/)
- [RBI Notifications](https://www.rbi.org.in/)
- [SEBI Circulars](https://www.sebi.gov.in/)

**Source Type**
- Websites + PDF circulars

**Ingestion Method**
- Scheduled ingestion (weekly/monthly)
- Metadata tagging by ministry + date

---

## 4. Legal Case Law Repositories (Secondary but Very Useful)

These sources provide **convenient indexing and citations**, but may not always be considered fully authoritative compared to official court portals.

---

### 4.1 Indian Kanoon

**Source**
- [Indian Kanoon](https://indiankanoon.org/)

**Source Type**
- Legal database website
- HTML judgments

**Content Available**
- Supreme Court, High Courts, tribunals, and district court orders
- Citations
- Related judgments
- Search query interface

**Ingestion Strategy**
- Use as a supplementary index
- Prefer linking back to official sources when possible
- Avoid bulk scraping unless allowed by policy/terms

---

### 4.2 LiveLaw (News + Case Updates)

**Source**
- [LiveLaw](https://www.livelaw.in/)

**Source Type**
- News + case summaries

**Use in Vidhi**
- Not primary evidence
- Can be used for trend analysis and recent updates
- Useful for citation discovery

---

### 4.3 Bar and Bench

**Source**
- [Bar and Bench](https://www.barandbench.com/)

**Use in Vidhi**
- Similar to LiveLaw
- Helpful for discovery, not authoritative judgment text

---

## 5. Government & Public Legal Portals

---

### 5.1 National Portal of India

**Source**
- [National Portal](https://www.india.gov.in/)

**Source Type**
- Government directory of resources

**Usage**
- Useful for discovering new official portals
- Index of ministry resources

---

### 5.2 National Judicial Data Grid (NJDG)

**Source**
- [NJDG](https://njdg.ecourts.gov.in/)

**Source Type**
- Dashboard + analytics

**Content Available**
- Pending case statistics
- Disposal rates
- Court-level metrics

**Usage in Vidhi**
- Used for analytics dashboards
- Not used for case-level documents

---

## 6. International & Comparative Law (Optional Enhancement)

Not required for core Vidhi, but can help in constitutional or treaty-related matters.

Examples:
- [WorldLII](http://www.worldlii.org/)
- [UN Treaty Collection](https://treaties.un.org/_

---

## 7. Public Legal Datasets and Bulk Downloads

These sources help build training/evaluation datasets.

---

### 7.1 Open Government Data Platform India

**Source**
- [data.gov.in](https://data.gov.in/)

**Source Type**
- Dataset portal (CSV/JSON)

**Usage**
- Legal statistics
- Court pendency analysis
- Ministry compliance datasets

---

### 7.2 Kaggle Legal Datasets (Supplementary)

**Source**
- [Kaggle](https://www.kaggle.com/datasets)

**Source Type**
- Community datasets

**Usage**
- Only for experimentation and evaluation
- Must validate licensing

---

## 8. Academic & Research Papers (Secondary)

These sources are not case law, but useful for understanding legal principles.

---

### 8.1 SCC Online Blog / Legal Commentary (Restricted Use)

**Source**
- SCC Online  
  https://www.scconline.com/

**Note**
- Commercial database (paid)
- Cannot be scraped without legal access
- Useful if user has subscription and uploads documents

---

### 8.2 JSTOR / Google Scholar / ResearchGate

Sources:
- [Google Scholar](https://scholar.google.com/)
- [JSTOR](https://www.jstor.org/)

Usage:
- Academic references
- Not treated as binding legal precedent

---

## 9. Legal Books, Digests, and Journals (Offline / User Upload)

Some lawyers rely on standard digests like:

- Mulla (CPC)
- Ratanlal & Dhirajlal (IPC)
- Sarkar Evidence Act
- Commentaries on Contract Act, NI Act, Arbitration Act

**Source Type**
- Physical books or scanned PDFs

**Ingestion Strategy**
- Only via user upload
- Must respect copyright
- Store locally with access controls

---

## 10. User Uploaded Documents (High Value Input Source)

Users may upload:

- FIR copies
- Charge sheets
- Court notices
- Affidavits
- Prior judgments
- Contracts / agreements
- Legal notices

**Source Type**
- PDF / DOCX / scanned images

**Ingestion Method**
- Upload handler
- OCR (if scanned)
- Sensitive data masking
- Session-based storage retention

**Security Requirements**
- Encrypt stored documents
- Auto-delete after configured retention
- Do not index personal sensitive content without consent

---

## 11. Document Formats Expected

Vidhi ingestion pipeline must support:

- PDF (digital + scanned)
- HTML pages
- DOCX (uploaded)
- TXT files
- Image scans (JPG/PNG)

---

## 12. Metadata Fields to Capture (Critical for Citation & Search)

Each case document should extract:

- Court name
- Bench / judge names
- Date of judgment
- Case number
- Parties
- Advocate names (if present)
- Sections / Acts cited
- Headnotes (if available)
- Citations (AIR, SCC, CriLJ, etc.)
- Related judgments referenced

---

## 13. Preferred Source Priority Order

Vidhi should follow a strict preference ranking:

1. Official Court Portals (SCI/HC/Tribunals)
2. India Code + Gazette
3. eCourts Services
4. Indian Kanoon (index + fallback)
5. News portals (LiveLaw/Bar&Bench)
6. Academic papers
7. User uploads

This ensures credibility and reduces hallucination risks.

---

## 14. Compliance Notes & Legal Considerations

### Key Rules
- Always store the source URL for every ingested document.
- Never fabricate citations.
- Ensure human review before document finalization.
- Avoid scraping sources with restricted terms unless explicit permission exists.

### Robots & Rate Limits
All scrapers must include:
- rate limiting
- exponential backoff
- caching
- respect for robots.txt (if applicable)

---

## 15. Output of Ingestion (Artifacts Stored)

Once ingestion completes, Vidhi generates:

- Cleaned text corpus (`data/processed/cleaned_text/`)
- Extracted metadata (`data/processed/extracted_metadata/`)
- Chunked text (`data/chunks/chunked_text/`)
- Chunk metadata (`data/chunks/chunk_metadata/`)
- Vector embeddings in:
  - FAISS (`vectorstore/faiss_index/`)
  - ChromaDB (`vectorstore/chroma_db/`)

---

## 16. Summary

Vidhi’s research accuracy depends heavily on the quality of legal sources. This document provides a structured source inventory so that ingestion pipelines can be built with:

- reliable sources
- scalable ingestion design
- ethical compliance
- strong citation traceability

---

## References (Primary Links)

- [Supreme Court of India](https://www.sci.gov.in/)
- [eCourts Portal: https](//ecourts.gov.in/)
- [eCourts Services](https://services.ecourts.gov.in/)
- [India Code](https://www.indiacode.nic.in/)
- [Gazette of India](https://egazette.nic.in/)
- [NCLT](https://nclt.gov.in/)
- [NCLAT](https://nclat.nic.in/)  
- [ITAT](https://itat.gov.in/)
- [NGT](https://greentribunal.gov.in/)
- [NCDRC](https://ncdrc.nic.in/)
- [Indian Kanoon](https://indiankanoon.org/)
- [Open Government Data](https://data.gov.in/)
- [NJDG](https://njdg.ecourts.gov.in/)
