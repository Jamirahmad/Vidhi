# Vidhi — Legal Research & Document Automation Platform

Vidhi is an assistive legal research and document automation platform tailored for the Indian legal ecosystem. It combines retrieval-augmented generation (RAG), structured prompting, and human-in-the-loop validation to support legal professionals in research and drafting workflows.

> ⚠️ Vidhi is **not a source of legal advice**. All outputs must be reviewed by a qualified professional.

---

## 🚀 Key Features

- 🔍 Legal research powered by RAG (LangChain + vector store)
- 🧠 Structured prompt orchestration for consistent outputs
- 📄 Document drafting assistance
- 📚 Knowledge base ingestion from public legal sources
- ⚡ FastAPI backend with modular services
- 💻 Modern React frontend (Vite-based)
- 🧩 Shared contract schemas for type safety

---

## 🏗️ Monorepo Structure

```
Vidhi/
├── backend/
├── frontend/
├── packages/
├── docs/
├── scripts/
├── tests/
├── deploy/
└── .env.example
```

---

## 🧠 Architecture Overview

Vidhi consists of three main layers:

### 1. Frontend
- Built with **React + Vite**

### 2. Backend (FastAPI)
- API gateway and orchestration layer

### 3. Knowledge Layer (RAG)
- LangChain-based pipeline
- Chroma vector store

---

## 📦 Setup Instructions

### Backend

```
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

```
pytest
```

---

## 🚢 Deployment

```
./deploy.sh
```

---

## 🛠️ Tech Stack

- React + Vite
- FastAPI
- LangChain
- Chroma
- Python, TypeScript

---

## ⚠️ Disclaimer

Vidhi is an assistive tool and does not replace professional legal advice.
