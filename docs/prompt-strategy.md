# Vidhi Prompt Strategy

This document describes how prompt modularization works in Vidhi and what safety layers are applied before and after model calls.

## 1) Goals

- Keep prompts **modular and reusable** across agent workflows.
- Keep generation **schema-oriented** and machine-consumable (JSON-first).
- Reduce unsafe or fabricated outputs through **defense-in-depth guardrails**.

## 2) Prompt modularization design

### 2.1 Core system prompt stack

Vidhi assembles a base system prompt from three core files:

- `backend/app/prompts/core/system.txt` (role + mission)
- `backend/app/prompts/core/safety.txt` (safety rules and non-fabrication)
- `backend/app/prompts/core/output_contract.txt` (strict output contract)

The composition is performed by `build_system_prompt()` in `backend/app/prompts/builder.py`.

### 2.2 Task prompt modules

Task-specific instructions are stored in `backend/app/prompts/modules/*.txt` and registered in:

- `backend/app/prompts/registry.py` via `TASK_PROMPT_FILES`
- `backend/app/prompts/types.py` via `PromptTaskName`

This design enables each agent endpoint to reference a stable task key (`issue_spotter`, `case_finder`, etc.) while keeping prompt text isolated from route code.

### 2.3 Prompt resolution at runtime

`backend/app/services/prompt_service.py` applies the following runtime logic:

1. `resolve_system_prompt()` builds the composed system prompt from core layers.
2. `resolve_task_prompt(task_or_prompt)`:
   - resolves known task keys through the registry, or
   - treats unknown input as raw prompt text (fallback behavior).

## 3) Safety and validation layers (defense in depth)

Vidhi applies guardrails across multiple stages:

### 3.1 Pre-LLM controls

- **Request model validation** (`backend/app/request_models.py`) enforces typed payload structure.
- **Prompt safety baseline** from `safety.txt` constrains hallucinations and legal-risk behavior.
- **Output contract instruction** from `output_contract.txt` requires JSON-only responses.

### 3.2 LLM request shaping controls

In `llm_json()` (`backend/app/main.py`):

- system prompt and resolved task prompt are sent separately,
- payload is normalized into a dictionary,
- provider request explicitly sets `response_format = {"type": "json_object"}`.

These controls bias the model toward deterministic, parseable responses.

### 3.3 Post-LLM controls

After provider response:

- response content is parsed with `json.loads`,
- non-JSON provider output raises `INVALID_PROVIDER_RESPONSE`,
- normalized error payloads are returned via centralized exception middleware.

## 4) Agent mapping strategy

Each agent endpoint under `/api/v1/agents/*` calls `llm_json(task_name, payload)`, where `task_name` maps to a registered prompt module. This keeps:

- endpoint code thin,
- prompt behavior configurable via prompt files,
- task behavior versionable by changing module text.

## 5) Operational recommendations (next maturity step)

To improve enterprise readiness further:

1. Add prompt version metadata (e.g., `version`, `owner`, `last_reviewed`) per module.
2. Add golden tests for prompt-output contracts by task.
3. Introduce policy checks for forbidden claims/format drift.
4. Track prompt revisions in changelog/release notes.

## 6) Related files

- `backend/app/prompts/builder.py`
- `backend/app/prompts/registry.py`
- `backend/app/prompts/types.py`
- `backend/app/services/prompt_service.py`
- `backend/app/main.py`
- `backend/app/request_models.py`
