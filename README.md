# 🚀 Vidhi – Intelligent Agent System for Structured Knowledge & Prompt Orchestration

## 📌 Overview

**Vidhi** is an enterprise-grade AI agent backend designed to orchestrate **modular prompts, knowledge retrieval, and service workflows** in a scalable and production-ready architecture.

It enables:

* Structured prompt engineering
* Knowledge-driven responses
* Extensible agent workflows
* Strong contract-based communication (TypeScript)

---

## 🧠 Key Capabilities

* 🔹 **Modular Prompt Architecture** – Reusable, composable prompt components
* 🔹 **Knowledge Integration Layer** – Supports embeddings & contextual retrieval
* 🔹 **Service-Oriented Design** – Clean orchestration via service layer
* 🔹 **Contract-Driven Development** – Shared schemas across systems
* 🔹 **Extensible Agent Framework** – Easily add new workflows/modules

---

## 🏗️ System Architecture

```
Client / API Layer
        │
        ▼
   Service Layer  ─────────────┐
        │                      │
        ▼                      ▼
 Prompt Builder          Knowledge Layer
 (Modular System)        (Embeddings/Data)
        │                      │
        └──────────────┬───────┘
                       ▼
                Response Engine
```

### 🔍 Core Components

| Component     | Description                                    |
| ------------- | ---------------------------------------------- |
| **Services**  | Orchestrates workflows and business logic      |
| **Prompts**   | Modular prompt templates and builders          |
| **Knowledge** | Handles embeddings, retrieval, and context     |
| **Contracts** | Shared TypeScript schemas for interoperability |

---

## 📁 Project Structure

```
backend/
  app/
    knowledge/        # Knowledge retrieval & embeddings
    prompts/          # Prompt modules and builder system
    services/         # Business logic & orchestration
    main.py           # Entry point

packages/
  contracts/          # Shared TypeScript interfaces
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```
git clone <your-repo-url>
cd vidhi
```

### 2. Setup Environment

```
cp .env.example .env
```

Update environment variables as needed.

---

### 3. Install Dependencies

**Python backend**

```
pip install -r requirements.txt
```

**TypeScript contracts**

```
cd packages/contracts
npm install
```

---

### 4. Run the Application

```
python backend/app/main.py
```

---

## 🔌 API Usage (Example)

```
POST /generate
```

**Request**

```json
{
  "input": "Sample query",
  "context": {}
}
```

**Response**

```json
{
  "output": "Generated response"
}
```

---

## 🧩 Prompt System Design

Vidhi uses a **layered prompt architecture**:

* `core/` → Base system prompts
* `modules/` → Feature-specific prompts
* `builder.py` → Dynamic composition engine
* `registry.py` → Central prompt management

### Benefits:

* Reusability
* Consistency
* Safety control
* Easy experimentation

---

## 🧪 Testing (Planned)

* Unit tests for services
* Prompt output validation
* Integration tests for workflows

---

## 🔄 CI/CD (Planned)

* Linting & formatting checks
* Automated test execution
* Build validation

---

## 🐳 Deployment (Planned)

* Dockerized backend
* Scalable deployment setup
* Environment-based configurations

---

## 🔐 Security Considerations

* Environment-based configuration (.env)
* No hardcoded secrets
* Input validation via request models

---

## 📈 Future Enhancements

* Prompt versioning & evaluation framework
* Multi-agent orchestration
* Observability (logging, metrics)
* Caching & performance optimization
* Queue-based async processing

---

## 🤝 Contributing

Contributions are welcome!
Please follow standard coding practices and raise a PR with clear descriptions.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Jamirahmad Mulla**
Senior Manager | Solution Architect | AI/ML Enthusiast

---
