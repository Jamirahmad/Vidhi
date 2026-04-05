from __future__ import annotations

from backend.app.prompts.registry import read_core_prompt


def build_system_prompt() -> str:
    parts = [
        read_core_prompt("system.txt"),
        read_core_prompt("safety.txt"),
        read_core_prompt("output_contract.txt"),
    ]
    return " ".join([part for part in parts if part])
