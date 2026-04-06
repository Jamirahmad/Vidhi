from __future__ import annotations

from typing import Any, Dict

VALID_PROMPT_OUTPUTS: Dict[str, Dict[str, Any]] = {
    "issue_spotter": {"issues": [{"id": "i1", "title": "Issue", "statute": "S138", "rationale": "facts"}]},
    "case_finder": {"precedents": [{"citation": "(2021) 1 SCC 1", "title": "Case"}]},
    "limitation_checker": {
        "assessment": {
            "inTime": True,
            "limitationWindowDays": 90,
            "computedDeadline": "2026-12-01",
            "rationale": "within limitation",
        }
    },
    "argument_builder": {"argumentSet": {"supporting": [], "opposing": [], "riskNotes": []}},
    "doc_composer": {"draft": {"documentType": "notice", "language": "en", "content": "draft text", "citations": []}},
    "compliance_guard": {"findings": [{"ruleId": "R1", "status": "ok", "message": "clear"}]},
    "aid_connector": {"aid": {"eligible": True, "providers": [], "notes": []}},
    "judgment_summarizer": {
        "summary": {
            "caseTitle": "A vs B",
            "court": "SC",
            "decision": "allowed",
            "plainLanguageSummary": "Summary",
        }
    },
    "knowledge_drilldown": {"analysis": {"summary": "grounded", "citedSourceIds": ["s1"], "citationNotes": []}},
    "provision_lookup": {"analysis": {"applicableProvisionIds": ["p1"], "citedSourceIds": ["p1"]}},
}
