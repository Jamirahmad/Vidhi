# Scope and Boundaries

## 1. Overview

Vidhi is an **assistive legal research and document automation platform** designed to streamline workflows in the Indian legal system.  
It aims to reduce manual effort for legal professionals, junior lawyers, and litigants by providing structured research outputs and draft documents.

This document defines **what Vidhi covers (Scope)** and **what it does not (Boundaries / Non-Goals)**.

---

## 2. Scope

### 2.1 Legal Research
- Retrieval of **Supreme Court, High Court, and Tribunal case laws**.  
- Identification of **legal issues, IPC/CrPC/CPC sections**, and key facts.  
- Access to **official legal databases**, open-source repositories, and publicly available judgments.  
- Semantic search using **vector stores** (ChromaDB / FAISS) for fast, relevant retrieval.  

### 2.2 Document Automation
- Drafting **bail applications, civil suits, notices, affidavits, and petitions**.  
- Incorporation of **court-specific formatting, annexures, and citations**.  
- Suggestion of **alternative arguments** based on precedents.

### 2.3 Compliance and Verification
- Check filings for **court rules and formatting compliance**.  
- Human-in-the-loop verification for all drafts and outputs.  
- Alerts for **time-barred or limitation issues**.

### 2.4 Multi-Agent Orchestration
- Coordinated execution of agents:
  - **CaseFinder** – Precedent retrieval  
  - **IssueSpotter** – Legal issue identification  
  - **LimitationChecker** – Time-bar analysis  
  - **ArgumentBuilder** – Arguments & counter-arguments  
  - **DocComposer** – Document generation  
  - **ComplianceGuard** – Compliance & formatting  
  - **AidConnector** – Legal aid suggestions  

### 2.5 Multilingual Support
- Outputs available in **English, Hindi, and regional languages**.  
- Translation of case facts, documents, and arguments while maintaining legal terminology.

---

## 3. Boundaries / Non-Goals

### 3.1 Legal Advice
- Vidhi **does not provide legal opinions**.  
- Outputs are **drafts or research assistance**, not professional advice.

### 3.2 Court Representation
- Vidhi **cannot represent users in court** or file petitions on their behalf.  

### 3.3 Novel Legal Questions
- For issues with **no prior precedents**, Vidhi may **flag gaps** but cannot generate assumptions.  

### 3.4 Data Limitations
- Only **verified and publicly available legal data** is ingested.  
- Sensitive or confidential client data must be **manually input and verified** by users.  

### 3.5 Liability
- Users are responsible for all **filings, submissions, and legal actions** based on Vidhi outputs.  

### 3.6 Scope of Automation
- Drafts require **human review and customization** before filing.  
- Full automation of legal processes, judgment analysis, or client interaction is **out of scope**.

---

## 4. Conclusion

Vidhi focuses on **assisting legal professionals** by providing structured research, insights, and document drafts while enforcing **human oversight and ethical boundaries**.  

It is a **tool for efficiency and accuracy**, not a replacement for legal expertise.  

> The boundaries defined here ensure that Vidhi remains a **responsible and safe platform** in the sensitive domain of law.

