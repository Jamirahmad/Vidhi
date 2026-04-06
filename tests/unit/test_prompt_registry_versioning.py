from backend.app.prompts.registry import get_prompt_manifest_version, get_task_prompt_versions


def test_prompt_manifest_version_is_exposed() -> None:
    version = get_prompt_manifest_version()

    assert isinstance(version, str)
    assert version


def test_task_prompt_versions_cover_all_registered_tasks() -> None:
    versions = get_task_prompt_versions()

    expected_tasks = {
        "knowledge_drilldown",
        "provision_lookup",
        "issue_spotter",
        "case_finder",
        "limitation_checker",
        "argument_builder",
        "doc_composer",
        "compliance_guard",
        "aid_connector",
        "judgment_summarizer",
    }

    assert set(versions.keys()) == expected_tasks
    assert all(version != "unversioned" for version in versions.values())
