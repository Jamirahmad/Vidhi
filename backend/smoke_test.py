import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent

for parent in [ROOT, *ROOT.parents]:
    env_file = parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

BASE_URL = os.getenv("VIDHI_API_BASE", "http://127.0.0.1:8000/api/v1")

SAMPLE_CASE = {
    "title": "Alpha Industries vs State Authority",
    "jurisdiction": "Delhi",
    "court": "Delhi High Court",
    "caseType": "civil",
    "facts": "Petitioner challenges a sector-specific levy as arbitrary and disproportionate under constitutional provisions and seeks interim relief.",
    "parties": [
        {"role": "petitioner", "name": "Alpha Industries"},
        {"role": "respondent", "name": "State Authority"},
    ],
}


def call(method: str, path: str, payload=None):
    with httpx.Client(timeout=60.0) as client:
        response = client.request(method, f"{BASE_URL}{path}", json=payload)
    try:
        data = response.json()
    except Exception:
        data = response.text
    return response.status_code, data


def main():
    status, data = call("GET", "/health")
    print("health", status, data)

    status, issues = call("POST", "/agents/issue-spotter", {"caseFacts": SAMPLE_CASE})
    print("issue-spotter", status, f"items={len(issues) if isinstance(issues, list) else 0}")
    if status >= 300 or not isinstance(issues, list) or len(issues) == 0:
        return

    status, precedents = call("POST", "/agents/case-finder", {"caseFacts": SAMPLE_CASE, "issues": issues})
    print("case-finder", status, f"items={len(precedents) if isinstance(precedents, list) else 0}")

    status, limitation = call("POST", "/agents/limitation-checker", {"caseFacts": SAMPLE_CASE, "issues": issues})
    print("limitation-checker", status, limitation)

    status, arguments = call(
        "POST",
        "/agents/argument-builder",
        {"caseFacts": SAMPLE_CASE, "issues": issues, "precedents": precedents if isinstance(precedents, list) else []},
    )
    print("argument-builder", status, arguments)

    status, draft = call(
        "POST",
        "/agents/doc-composer",
        {
            "caseFacts": SAMPLE_CASE,
            "issues": issues,
            "arguments": arguments if isinstance(arguments, dict) else {},
            "precedents": precedents if isinstance(precedents, list) else [],
            "preferredLanguage": "en",
        },
    )
    print("doc-composer", status, "ok" if status < 300 else draft)

    status, findings = call(
        "POST",
        "/agents/compliance-guard",
        {
            "caseFacts": SAMPLE_CASE,
            "draft": draft if isinstance(draft, dict) else {},
            "precedents": precedents if isinstance(precedents, list) else [],
        },
    )
    print("compliance-guard", status, f"items={len(findings) if isinstance(findings, list) else 0}")

    status, aid = call("POST", "/agents/aid-connector", {"caseFacts": SAMPLE_CASE})
    print("aid-connector", status, aid)

    status, kb = call("GET", f"/knowledge-base/search?q={quote('article 14')}")
    print("knowledge-base", status, f"items={len(kb) if isinstance(kb, list) else 0}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("smoke test failed", exc)
        sys.exit(1)
