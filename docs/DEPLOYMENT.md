## 1. Purpose

This document explains how to deploy **Vidhi** (multi-agent legal AI system) using **free-tier or minimal-cost infrastructure**.

It covers:

- Local setup (developer machine)
- Docker-based deployment
- AWS Free Tier deployment (recommended cloud option)
- Streamlit Cloud deployment (UI-only)
- Render / Replit deployment options
- Monitoring and operational tips

This deployment guide matches the repo structure under:

```
deployments/
  local/
  aws_free_tier/
  streamlit_cloud/
  render_replit/
scripts/
src/
```

---

## 2. Supported Deployment Modes

Vidhi can run in the following modes:

### 2.1 Local Development Mode (Recommended for development)

Runs everything locally:

- API (FastAPI)
- UI (Streamlit)
- Vector Store (FAISS or Chroma local)
- Storage (Local filesystem)

### 2.2 Docker Deployment Mode (Recommended for demo/prod simulation)

Runs using Docker Compose:

- API container
- UI container
- Optional vector store persistence volumes

### 2.3 AWS Free Tier Deployment (Recommended for cloud)

Runs on:

- EC2 Free Tier (t2.micro / t3.micro)
- S3 Free Tier (optional storage)
- Optional CloudWatch (minimal)

### 2.4 Streamlit Cloud Deployment (UI-focused)

Best for demo UI hosting, but backend API must still be hosted separately.

### 2.5 Render / Replit Deployment (quick public hosting)

Useful for showcasing, but not recommended for long-term production.

---

## 3. Deployment Components Mapping

| Component | Location in Repo | Deployment Target |
|----------|------------------|------------------|
| FastAPI Backend | `src/api/main.py` | Local / Docker / AWS |
| Streamlit UI | `src/ui/streamlit_app.py` | Local / Docker / Streamlit Cloud |
| Agents | `src/agents/` | Backend runtime |
| Orchestrator | `src/core/orchestrator.py` | Backend runtime |
| Retrieval | `src/retrieval/` | Backend runtime |
| Vector DB | `vectorstore/` | Local / Docker volume / EC2 disk |
| Data Ingestion | `src/ingestion/` | Local / EC2 scheduled jobs |
| Outputs | `outputs/` | Local / EC2 disk / S3 |

---

## 4. Environment Variables Setup

Vidhi uses environment-driven configuration.

A sample file exists:

```
.env.example
```

### 4.1 Create Local `.env`

Copy:

```bash
cp .env.example .env
```

### 4.2 Required Environment Variables

Minimal `.env` example:

```env
APP_ENV=local
LOG_LEVEL=INFO

OPENAI_API_KEY=your_key_here
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini

VECTOR_STORE=faiss
VECTORSTORE_PATH=vectorstore/faiss_index

DATA_DIR=data/
OUTPUT_DIR=outputs/
LOG_DIR=logs/

ENABLE_SAFETY_GUARDRAILS=true
ENABLE_CITATION_VALIDATION=true
ENABLE_HUMAN_HANDOFF=true
```

---

## 5. Local Deployment (No Docker)

### 5.1 Install Python

Recommended:

- Python 3.10+
- pip / venv enabled

Verify:

```bash
python --version
```

### 5.2 Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate     # Linux/Mac
.venv\Scripts\activate        # Windows
```

### 5.3 Install Dependencies

```bash
pip install -r requirements.txt
```

Or if using pyproject:

```bash
pip install -e .
```

### 5.4 Run FastAPI Backend

Option 1 (direct):

```bash
python -m src.api.main
```

Option 2 (uvicorn):

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should be available at:

```
http://localhost:8000
```

Health check:

```
http://localhost:8000/health
```

### 5.5 Run Streamlit UI

```bash
streamlit run src/ui/streamlit_app.py
```

UI should be available at:

```
http://localhost:8501
```

---

## 6. Local Deployment Using Scripts

Your repo already includes scripts:

```
scripts/run_api.sh
scripts/run_ui.sh
scripts/ingest_documents.sh
scripts/build_vectorstore.sh
```

Recommended flow:

### 6.1 Run API

```bash
bash scripts/run_api.sh
```

### 6.2 Run UI

```bash
bash scripts/run_ui.sh
```

### 6.3 Run Ingestion

```bash
bash scripts/ingest_documents.sh
```

### 6.4 Build Vector Store

```bash
bash scripts/build_vectorstore.sh
```

---

## 7. Docker Deployment (Local)

Docker deployment is available under:

```
deployments/local/docker-compose.yml
deployments/local/Dockerfile
```

### 7.1 Install Docker

Install:

- Docker Desktop (Windows/Mac)
- Docker Engine (Linux)

Verify:

```bash
docker --version
docker compose version
```

### 7.2 Run Docker Compose

From project root:

```bash
docker compose -f deployments/local/docker-compose.yml up --build
```

### 7.3 Expected Services

Once running:

- API → `http://localhost:8000`
- UI → `http://localhost:8501`

### 7.4 Stopping

```bash
docker compose -f deployments/local/docker-compose.yml down
```

---

## 8. AWS Free Tier Deployment (Recommended Cloud Option)

AWS is the best free-tier option for your architecture because:

- EC2 free-tier supports Python backend
- Storage can be local disk or S3
- You can persist vectorstore and data

This deployment aligns with:

```
deployments/aws_free_tier/
  ec2_setup_guide.md
  nginx_config.conf
  systemd_service.txt
  s3_bucket_structure.md
```

---

## 9. AWS Free Tier Architecture

### 9.1 Recommended Setup

| Service | Free Tier? | Usage |
|--------|------------|------|
| EC2 t2.micro/t3.micro | Yes | Run API + UI |
| EBS 30GB | Yes | Persist vector store + logs |
| S3 | Limited Free Tier | Store outputs + ingested PDFs |
| CloudWatch | Limited | Basic monitoring |

### 9.2 Suggested Deployment Model

EC2 runs:

- FastAPI backend (systemd service)
- Streamlit UI (systemd service or behind Nginx)

Nginx runs as reverse proxy:

- `/api` → FastAPI
- `/` → Streamlit

---

## 10. AWS EC2 Setup Steps

### 10.1 Launch EC2 Instance

- Choose Ubuntu 22.04 LTS
- Instance type: **t2.micro**
- Storage: 20–30GB
- Allow inbound ports:
  - 22 (SSH)
  - 80 (HTTP)
  - 443 (HTTPS)
  - 8501 (optional for Streamlit)
  - 8000 (optional for FastAPI)

Recommended: Only open **80/443** publicly.

---

### 10.2 Connect via SSH

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

---

### 10.3 Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git nginx
```

---

### 10.4 Clone Repo

```bash
git clone https://github.com/<your-org>/vidhi.git
cd vidhi
```

---

### 10.5 Setup Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 10.6 Configure `.env`

```bash
cp .env.example .env
nano .env
```

Update:

- OPENAI_API_KEY
- VECTORSTORE_PATH
- OUTPUT_DIR

---

### 10.7 Run API (Test)

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Visit:

```
http://EC2_PUBLIC_IP:8000/health
```

---

### 10.8 Run UI (Test)

```bash
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

Visit:

```
http://EC2_PUBLIC_IP:8501
```

---

## 11. Nginx Reverse Proxy Setup (Recommended)

Use the file:

```
deployments/aws_free_tier/nginx_config.conf
```

Copy into:

```bash
sudo nano /etc/nginx/sites-available/vidhi
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/vidhi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Now:

- UI accessible via port 80
- API accessible via `/api`

Example:

```
http://EC2_PUBLIC_IP/api/health
```

---

## 12. Systemd Services (Recommended)

Use:

```
deployments/aws_free_tier/systemd_service.txt
```

Create service for FastAPI:

```bash
sudo nano /etc/systemd/system/vidhi-api.service
```

Create service for Streamlit:

```bash
sudo nano /etc/systemd/system/vidhi-ui.service
```

Enable + start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vidhi-api
sudo systemctl enable vidhi-ui
sudo systemctl start vidhi-api
sudo systemctl start vidhi-ui
```

Check status:

```bash
sudo systemctl status vidhi-api
sudo systemctl status vidhi-ui
```

---

## 13. Storage Strategy (Free Tier Friendly)

### 13.1 Local Storage (Default)

Best for free tier.

Data stored under:

```
data/
outputs/
vectorstore/
logs/
```

Pros:
- Fast
- Simple
- No cloud cost

Cons:
- Instance loss = data loss unless backed up

---

### 13.2 S3 Storage (Optional)

S3 structure should follow:

```
deployments/aws_free_tier/s3_bucket_structure.md
```

Use S3 for:

- ingested PDFs
- generated documents
- audit logs backups

Avoid using S3 for vectorstore directly unless optimized.

---

## 14. Streamlit Cloud Deployment

This aligns with:

```
deployments/streamlit_cloud/
  streamlit_requirements.txt
  streamlit_cloud_deploy.md
```

### 14.1 Best Practice

Streamlit Cloud should only host UI.

Backend should be deployed separately on:

- AWS EC2
- Render

Update UI configuration:

- Set API base URL in `.env`
- Streamlit calls backend via REST

---

## 15. Render / Replit Deployment

This aligns with:

```
deployments/render_replit/
  render_deploy.md
  replit_deploy.md
```

### 15.1 Render

Render is good for hosting FastAPI backend quickly.

But note:

- free-tier sleeping instances
- vectorstore persistence is limited
- not good for large ingestion pipelines

### 15.2 Replit

Good for:

- hackathon demos
- rapid prototype

Not recommended for production due to compute limits.

---

## 16. Recommended Free-Tier Setup (Best Combination)

For your use case, the best free-tier deployment is:

### Option A (Best Overall)

- AWS EC2 Free Tier → backend + vector store + ingestion
- Streamlit Cloud → UI
- S3 Free Tier → outputs + PDF storage

This gives:

- public UI access
- stable backend
- persistent vectorstore

### Option B (All-in-One on EC2)

- AWS EC2 Free Tier → UI + backend + vector store

Simpler, but may be slow due to EC2 memory limits.

---

## 17. Deployment Checklist

### 17.1 Pre-Deployment Checklist

- `.env` configured
- vectorstore built (FAISS/Chroma)
- ingestion pipeline tested locally
- API endpoints validated via tests
- UI tested locally

### 17.2 Post-Deployment Checklist

- `/health` endpoint working
- UI loads and can submit a case query
- Retrieval returns citations
- Safety guardrails enabled
- Logs written under `logs/`
- Outputs generated under `outputs/`

---

## 18. Monitoring & Logs

Logs are written under:

```
logs/
  app.log
  retrieval.log
  agent_traces.log
```

On EC2, check:

```bash
tail -f logs/app.log
tail -f logs/agent_traces.log
```

Systemd logs:

```bash
journalctl -u vidhi-api -f
journalctl -u vidhi-ui -f
```

---

## 19. Scaling Considerations (Future)

Free-tier will support only:

- small ingestion
- light concurrent usage
- demo-level workload

For scaling:

- move vectorstore to managed DB
- move ingestion pipeline to batch jobs
- enable caching layer (Redis)
- deploy agents as separate services if needed

---

## 20. Security Recommendations

Minimum steps:

- Never commit `.env`
- Rotate API keys
- Enable HTTPS using Let's Encrypt
- Restrict inbound ports (only 80/443)
- Enable rate limiting middleware (`src/api/middleware/rate_limiter.py`)
- Enable compliance agent (CCA) in production

---

## 21. Recommended Free-Tier Platforms Summary

| Platform | Recommended For | Notes |
|---------|------------------|------|
| AWS EC2 Free Tier | Best overall deployment | Supports backend + ingestion |
| Streamlit Cloud | UI hosting | Needs backend hosted separately |
| Render | quick API hosting | free tier sleeps |
| Replit | prototype | limited persistence |
| Local Docker | dev + testing | easiest for demos |

---

## 22. References (Repo-Specific)

This deployment guide directly relates to:

- `deployments/local/docker-compose.yml`
- `deployments/aws_free_tier/ec2_setup_guide.md`
- `deployments/aws_free_tier/nginx_config.conf`
- `deployments/aws_free_tier/systemd_service.txt`
- `deployments/aws_free_tier/s3_bucket_structure.md`
- `scripts/run_api.sh`
- `scripts/run_ui.sh`
