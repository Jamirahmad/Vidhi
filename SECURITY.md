# Security Policy

## Supported Versions

Vidhi is currently in active development as a capstone project.  
Security fixes and updates are applied only to the latest version available in the `main` branch.

| Version | Supported |
|---------|----------|
| Latest (`main`) | ✅ Yes |
| Older versions | ❌ No |

---

## Reporting a Vulnerability

If you discover a security vulnerability in Vidhi, please report it responsibly.

### Please DO NOT:
- Open a public GitHub issue for security vulnerabilities
- Share exploit steps publicly
- Publish sensitive system details or user data

### Please DO:
Send a private report to the project maintainers.

📩 Contact Email: **jamirahmadmulla@gmail.com**

Include the following details in your report:

- Vulnerability type (example: prompt injection, data leakage, API key exposure)
- Steps to reproduce the issue
- Potential impact (data exposure, unsafe output, unauthorized access)
- Logs/screenshots (if applicable)
- Suggested mitigation (if you have one)

---

## Response Timeline

We aim to respond within:

- **3–5 days** for acknowledgment
- **7–14 days** for investigation and fix (depending on complexity)

---

## Security Considerations for Vidhi

Vidhi deals with legal research and document drafting workflows.  
The following risks are considered high priority:

### 1. Prompt Injection Attacks
Attackers may try to manipulate agent prompts to:
- override safety rules
- fabricate citations
- leak internal instructions
- bypass human verification steps

Mitigation expected:
- strict prompt templates
- output validation rules
- human handoff enforcement

---

### 2. Hallucinated Case Laws / Fake Citations
Generating non-existent judgments is a critical risk.

Mitigation expected:
- citation verification pipeline
- retrieval-first approach (RAG)
- warnings for low-confidence outputs

---

### 3. Sensitive User Data Leakage
Users may provide private case facts and personal details.

Mitigation expected:
- avoid storing user inputs unless explicitly required
- avoid logging raw sensitive inputs
- redact personally identifiable information (PII) where possible

---

### 4. API Key and Secret Exposure
Misconfigured deployments can leak API keys.

Mitigation expected:
- `.env` based configuration
- `.gitignore` protection
- secrets must never be committed

---

### 5. Unsafe Legal Misuse
Vidhi must not be used to:
- provide legal advice
- guarantee outcomes
- misrepresent legal facts
- enable unethical or illegal activities

Mitigation expected:
- disclaimers
- safety guardrails
- refusal rules for out-of-scope tasks

---

## Safe Development Guidelines

All contributors must follow these rules:

- Never hardcode credentials or API keys
- Always use `.env` files for secrets
- Do not commit court dataset dumps unless licensing is verified
- Ensure all generated documents include a disclaimer
- Add validation checks to prevent fabricated citations
- Ensure agents stop and hand off to humans for final decisions

---

## Dependency Security

We recommend contributors regularly check for vulnerable dependencies:

```bash
pip install pip-audit
pip-audit
```

---

## Disclosure Policy
Once a vulnerability is confirmed and fixed, maintainers may:

- document the fix in `CHANGELOG.md`
- mention it in a GitHub release note
- credit the reporter (only if requested)

---

## Final Note
Vidhi is an educational and research project.
However, because it operates in a sensitive legal domain, we treat security, privacy, and ethical safeguards as core requirements.

Thank you for helping keep Vidhi safe.
