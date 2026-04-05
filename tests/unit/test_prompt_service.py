from backend.app.services.prompt_service import resolve_system_prompt, resolve_task_prompt


def test_resolve_system_prompt_includes_core_contracts() -> None:
    system_prompt = resolve_system_prompt()

    assert "You are Vidhi" in system_prompt
    assert "Do not fabricate" in system_prompt
    assert "Return JSON only" in system_prompt


def test_resolve_task_prompt_for_registered_task() -> None:
    task_prompt = resolve_task_prompt("issue_spotter")

    assert "Task" in task_prompt
    assert "issues" in task_prompt.lower()


def test_resolve_task_prompt_passthrough_for_custom_prompt() -> None:
    custom = "custom analysis instructions"

    assert resolve_task_prompt(custom) == custom
    assert resolve_task_prompt("") == ""
