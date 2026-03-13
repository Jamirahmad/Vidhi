"""Shared Streamlit session-state helpers for application workflow."""

from __future__ import annotations

from typing import Any

import streamlit as st


def ensure_state() -> None:
    st.session_state.setdefault("registered_cases", [])
    st.session_state.setdefault("latest_citations", [])


def register_case(case_data: dict[str, Any]) -> None:
    ensure_state()
    existing = st.session_state["registered_cases"]
    case_id = case_data.get("case_id")
    if case_id and not any(item.get("case_id") == case_id for item in existing):
        existing.append(case_data)


def get_registered_cases() -> list[dict[str, Any]]:
    ensure_state()
    return list(st.session_state["registered_cases"])


def set_latest_citations(citations: list[dict[str, Any]]) -> None:
    ensure_state()
    st.session_state["latest_citations"] = citations


def get_latest_citations() -> list[dict[str, Any]]:
    ensure_state()
    return list(st.session_state["latest_citations"])
