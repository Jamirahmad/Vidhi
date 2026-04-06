from backend.app.prompts.builder import build_system_prompt


def test_build_system_prompt_contains_all_core_sections() -> None:
    prompt = build_system_prompt()

    assert "You are Vidhi" in prompt
    assert "Safety" in prompt
    assert "JSON" in prompt
