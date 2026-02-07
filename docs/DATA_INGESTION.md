## 1. Purpose of Data Ingestion in Vidhi

Vidhi depends on **retrieval-augmented generation (RAG)**.  
Instead of relying on the LLM alone, Vidhi retrieves real case laws and statutes from its knowledge base.

The ingestion pipeline ensures:

- Court judgments are captured from trusted sources
- PDFs/HTML pages are converted into clean text
- Metadata is extracted (court, year, case number, citations, judges, acts, sections)
- Content is chunked for retrieval performance
- Embeddings are generated for similarity search
- FAISS/ChromaDB is built and persisted for reuse

---

## 2. Supported Data Sources

Vidhi supports ingestion from the following legal sources:

### A) Public Court Sources
- Supreme Court of India judgments
- High Court portals (state-specific)
- Tribunal websites (NCLT, NCLAT, ITAT, CAT, consumer courts)

### B) Open Legal Databases (Optional / Community Driven)
- Indian Kanoon (only if usage policy allows; should not violate ToS)
- Open government legal archives
- Law commission and legislative portals

### C) User Uploads
- PDFs uploaded by lawyers/litigants
- Word/HTML copies of judgments
- scanned legal documents (OCR supported)

---

## 3. High-Level Ingestion Workflow

The ingestion pipeline follows this flow:

1. **Fetch** legal documents (scraping/API/manual upload)
2. **Parse** documents (PDF, HTML, scanned images)
3. **Clean** extracted text (remove noise, headers, page numbers)
4. **Detect language** (English/Hindi/Regional)
5. **Extract metadata** (court, bench, date, case number, citations)
6. **Chunk** content into semantically meaningful segments
7. **Generate embeddings**
8. **Store in vector database** (FAISS or ChromaDB)
9. **Persist vector store** for reuse by retrieval agents

---

## 4. Repository Modules for Ingestion

### Core ingestion code
Located at:

```
src/ingestion/
```

Key submodules:

- `fetchers/` → download / scrape sources
- `parsers/` → parse PDF/HTML/OCR documents
- `cleaners/` → remove noise and standardize text
- `chunking/` → split text into retrieval-ready chunks
- `metadata/` → extract structured metadata fields
- `pipelines/` → orchestration and execution runner

---

## 5. Data Storage Locations

Vidhi maintains structured storage for all ingestion stages.

### Raw downloads
```
data/raw/
  sc/
  hc/
  tribunals/
  user_uploads/
```

### Processed clean text and metadata
```
data/processed/
  cleaned_text/
  extracted_metadata/
```

### Chunk outputs
```
data/chunks/
  chunked_text/
  chunk_metadata/
```

---

## 6. Chunking Strategy (Important for RAG Accuracy)

Chunking is critical for legal documents because judgments are long and contain multiple sections.

### Recommended Chunk Rules
- chunk size: **500–1200 tokens**
- overlap: **100–200 tokens**
- preserve headings like:
  - Facts
  - Issues
  - Arguments
  - Observations
  - Judgment / Order
  - Case citations

### Output per chunk
Each chunk stored in the vector store should include:

- `chunk_id`
- `source_doc_id`
- `court`
- `case_title`
- `citation`
- `judgment_date`
- `judge`
- `act_sections`
- `language`
- `chunk_text`

---

## 7. Metadata Extraction

Metadata is extracted to support:

- filtering by jurisdiction (Delhi HC, Bombay HC, SC)
- filtering by year range (e.g., last 20 years)
- filtering by domain (criminal/civil)
- verifying citations in generated outputs

Typical extracted metadata fields:

- Court name
- State
- Case number
- Parties
- Date of judgment
- Judge/bench
- IPC/CrPC/CPC sections mentioned
- Key citations and references
- Outcome summary (optional)

---

## 8. Embedding Generation

Embeddings convert each chunk into a numerical vector.

Vidhi supports:

- OpenAI embeddings (recommended for quality)
- HuggingFace embeddings (free-tier option)

Embedding is performed inside:

```
src/retrieval/embedding_provider.py
```

---

## 9. Vector Store Build (FAISS / ChromaDB)

Vidhi supports both:

### Option A: FAISS (Local-first, Fast)
- best for local deployment
- stored on disk as FAISS index

Stored at:

```
vectorstore/faiss_index/
```

### Option B: ChromaDB (Persistent + Easy Filtering)
- supports metadata filtering
- good for prototyping and free-tier deployment

Stored at:

```
vectorstore/chroma_db/
```

Vector store management is implemented in:

```
src/retrieval/vector_store_manager.py
src/retrieval/faiss_store.py
src/retrieval/chroma_store.py
```

---

## 10. Ingestion Pipeline Execution

Main runner:

```
src/ingestion/pipelines/ingestion_runner.py
```

### Typical pipeline execution steps

1. Fetch new documents
2. Parse and clean
3. Extract metadata
4. Chunk content
5. Generate embeddings
6. Store embeddings in FAISS/Chroma

---

## 11. Scripts for Ingestion & Vector Build

In `scripts/` folder:

```
scripts/ingest_documents.sh
scripts/build_vectorstore.sh
```

These scripts are used in:

- local development
- AWS Free Tier EC2 deployment
- CI/CD pipelines (optional)

---

## 12. Example: Local Ingestion & Vector Store Build

### Step 1: Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run ingestion
```bash
python -m src.ingestion.pipelines.ingestion_runner   --source sc   --output_dir data/processed
```

### Step 4: Build vector store
```bash
python -m src.retrieval.vector_store_manager   --input_dir data/chunks/chunked_text   --store chroma   --persist_dir vectorstore/chroma_db
```

---

## 13. Deployment Link: How Ingestion Fits into AWS Free Tier

### Recommended AWS Free Tier Setup
- EC2 t2.micro / t3.micro (Free Tier eligible)
- EBS storage for vectorstore persistence
- Optional S3 bucket for raw dataset storage

In AWS deployment:

- ingestion runs periodically (cron/systemd)
- vectorstore is rebuilt incrementally

### Typical flow on EC2
1. ingest new judgments into `data/raw/`
2. process + chunk into `data/chunks/`
3. update `vectorstore/`
4. restart API if needed

---

## 14. Deployment Link: How Ingestion Fits into Streamlit Cloud

Streamlit Cloud has limitations:
- no persistent local storage
- no large dataset hosting

So for Streamlit Cloud deployment:
- pre-build the vectorstore locally
- commit small sample index OR download from GitHub release
- use limited dataset for demo

Recommended:
- include only 50–200 sample judgments in demo mode

---

## 15. Recommended Free-Tier Strategy for Capstone Demo

For IITM capstone demonstration, recommended approach is:

### Approach A (Simplest)
- local ingestion + local FAISS/Chroma
- run Streamlit UI locally

### Approach B (Best Free Tier Cloud)
- AWS EC2 for API + ingestion + vectorstore
- Streamlit Cloud for UI frontend
- EC2 serves retrieval + document generation API

---

## 16. Incremental Ingestion Strategy (Important)

Legal databases are large, so full ingestion is unrealistic.

Recommended incremental strategy:

- Start with:
  - bail judgments (CrPC 437/439)
  - fraud cases (IPC 420, 467, 468, 471)
  - property disputes and limitation cases
- Expand dataset gradually

This makes vectorstore manageable and demo-ready.

---

## 17. Data Quality Controls

To avoid hallucinations and wrong citations:

### Mandatory checks
- each retrieved chunk must contain citation metadata
- citation validator ensures citation format exists
- retrieval agent returns the exact paragraph references
- doc generator must cite chunk IDs

---

## 18. Risks & Legal Considerations

### Risks
- scraped court sites may block automated requests
- OCR quality issues for scanned PDFs
- inconsistent metadata formats across courts
- possible missing or incomplete judgments

### Legal considerations
- respect court website terms of service
- do not redistribute copyrighted judgments improperly
- store only metadata + publicly available judgments for demo

---

## 19. Output Expectations for Retrieval Agents

Agents like `CaseFinder` and `LegalOrchestrator` should receive structured retrieval output:

Example JSON structure:

```json
{
  "query": "Delhi HC bail IPC 420 first-time offender",
  "top_matches": [
    {
      "case_title": "Sanjay Chandra v CBI",
      "citation": "(2012) 1 SCC 40",
      "court": "Supreme Court",
      "judgment_date": "2012-02-15",
      "chunk_id": "SC_2012_000123_chunk_07",
      "excerpt": "Bail is the rule and jail is the exception..."
    }
  ]
}
```

This is later used by the document drafting agent.

---

## 20. Summary

Vidhi ingestion and vector build pipeline is designed to be:

- modular
- scalable
- cloud deployable
- free-tier friendly
- safe and traceable for legal citation use

The ingestion pipeline ensures the system produces outputs based on real sources rather than hallucinated legal information.

---

## Related Documents

- `docs/DEPLOYMENT.md`
- `docs/design/agent_responsibilities.md`
- `docs/dataset/data_sources.md`
- `docs/dataset/ingestion_strategy.md`
- `docs/architecture/data_ingestion_pipeline.png`
- `docs/architecture/deployment_free_tier.png`

