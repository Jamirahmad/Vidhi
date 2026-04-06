from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from backend.app.prompts.types import PromptTaskName

_PROMPTS_DIR = Path(__file__).resolve().parent
_CORE_DIR = _PROMPTS_DIR / "core"
_MODULES_DIR = _PROMPTS_DIR / "modules"
_MANIFEST_PATH = _PROMPTS_DIR / "manifest.json"

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


def _read_manifest() -> Dict[str, Any]:
    return json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))


def read_core_prompt(name: str) -> str:
    return (_CORE_DIR / name).read_text(encoding="utf-8").strip()


def has_task_prompt(task: str) -> bool:
    return task in TASK_PROMPT_FILES


def read_task_prompt(task: PromptTaskName) -> str:
    filename = TASK_PROMPT_FILES[task]
    return (_MODULES_DIR / filename).read_text(encoding="utf-8").strip()


def get_prompt_manifest_version() -> str:
    manifest = _read_manifest()
    return str(manifest.get("manifestVersion", "unknown"))


def get_task_prompt_versions() -> Dict[PromptTaskName, str]:
    manifest = _read_manifest()
    modules = manifest.get("modules", {})
    versions: Dict[PromptTaskName, str] = {}
    for task, file_name in TASK_PROMPT_FILES.items():
        module = modules.get(task, {})
        if module.get("file") == file_name:
            versions[task] = str(module.get("version", "unversioned"))
            continue
        versions[task] = "unversioned"
    return versions
