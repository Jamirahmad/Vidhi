from __future__ import annotations

from pathlib import Path
from typing import Dict

from backend.app.prompts.types import PromptTaskName

_PROMPTS_DIR = Path(__file__).resolve().parent
_CORE_DIR = _PROMPTS_DIR / "core"
_MODULES_DIR = _PROMPTS_DIR / "modules"

TASK_PROMPT_FILES: Dict[PromptTaskName, str] = {
    "knowledge_drilldown": "knowledge_drilldown.txt",
    "provision_lookup": "provision_lookup.txt",
    "issue_spotter": "issue_spotter.txt",
    "case_finder": "case_finder.txt",
    "limitation_checker": "limitation_checker.txt",
    "argument_builder": "argument_builder.txt",
    "doc_composer": "doc_composer.txt",
    "compliance_guard": "compliance_guard.txt",
    "aid_connector": "aid_connector.txt",
    "judgment_summarizer": "judgment_summarizer.txt",
}


def read_core_prompt(name: str) -> str:
    return (_CORE_DIR / name).read_text(encoding="utf-8").strip()


def has_task_prompt(task: str) -> bool:
    return task in TASK_PROMPT_FILES


def read_task_prompt(task: PromptTaskName) -> str:
    filename = TASK_PROMPT_FILES[task]
    return (_MODULES_DIR / filename).read_text(encoding="utf-8").strip()
