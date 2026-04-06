from __future__ import annotations

from typing import Any, Dict

GOLDEN_VALID_CASES: Dict[str, Dict[str, Any]] = {
    "issue_spotter": {"issues": [{"id": "i1", "title": "Territorial jurisdiction", "statute": "CPC", "rationale": "Cause arose in forum"}]},
    "case_finder": {
        "precedents": [
            {
                "citation": "(2021) 1 SCC 1",
                "title": "Example v State",
                "court": "Supreme Court",
                "year": 2021,
                "relevanceScore": 0.92,
                "supports": "petitioner",
                "summary": "Summarized ratio",
                "sourceUrl": "https://example.org/case",
                "sourceName": "SCC",
            }
        ]
    },
    "limitation_checker": {
        "assessment": {
            "inTime": True,
            "limitationWindowDays": 90,
            "elapsedDays": 70,
            "excludedDays": 0,
            "effectiveElapsedDays": 70,
            "computedDeadline": "2026-08-15",
            "daysRemaining": 20,
            "rationale": "Filed within statutory limit",
            "assumptions": [],
            "checkpoints": [],
        }
    },
    "argument_builder": {"argumentSet": {"supporting": ["Ground A"], "opposing": ["Counter A"], "riskNotes": ["Risk A"]}},
    "doc_composer": {"draft": {"documentType": "notice", "language": "en", "content": "Draft body", "citations": ["(2021) 1 SCC 1"]}},
    "compliance_guard": {"findings": [{"ruleId": "R1", "status": "pass", "message": "No breach identified"}]},
    "aid_connector": {"aid": {"eligible": True, "providers": [{"name": "DLSA", "location": "Pune", "contact": "+91-000"}], "notes": []}},
    "judgment_summarizer": {
        "summary": {
            "caseTitle": "A v B",
            "court": "SC",
            "judgmentDate": "2026-01-10",
            "issues": ["Issue 1"],
            "decision": "Appeal allowed",
            "reasoning": "Reasoning text",
            "keyPoints": ["Point 1"],
            "plainLanguageSummary": "Plain summary",
            "citations": ["(2020) 2 SCC 3"],
        }
    },
    "knowledge_drilldown": {
        "analysis": {
            "summary": "Grounded summary",
            "keyPoints": ["point"],
            "nextSteps": ["step"],
            "citedSourceIds": ["src-1"],
            "citationNotes": [{"sourceId": "src-1", "note": "note"}],
        }
    },
    "provision_lookup": {
        "analysis": {
            "applicableProvisionIds": ["prov-1"],
            "plainLanguageSummary": "Applicable provisions explained",
            "howToApply": ["apply step"],
            "riskNotes": ["risk"],
            "citedSourceIds": ["prov-1"],
            "citationNotes": [{"sourceId": "prov-1", "note": "note"}],
        }
    },
}

GOLDEN_INVALID_CASES: Dict[str, Dict[str, Any]] = {
    "issue_spotter": {"issues": [{"id": "i1", "title": "Missing fields"}]},
    "case_finder": {"precedents": [{"title": "Missing citation"}]},
    "limitation_checker": {"assessment": {"inTime": "yes", "rationale": "wrong type + missing fields"}},
    "argument_builder": {"argumentSet": {"supporting": []}},
    "doc_composer": {"draft": {"documentType": "notice"}},
    "compliance_guard": {"findings": [{"ruleId": "R1"}]},
    "aid_connector": {"aid": {"eligible": True, "providers": [{}]}},
    "judgment_summarizer": {"summary": {"caseTitle": "A v B", "decision": "Allowed"}},
    "knowledge_drilldown": {"analysis": {"summary": "No citations"}},
    "provision_lookup": {"analysis": {"applicableProvisionIds": "prov-1"}},
}
