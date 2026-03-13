from src.core.api_orchestrator import Orchestrator


def test_api_orchestrator_is_importable_and_callable():
    orchestrator = Orchestrator()
    result = orchestrator.run_research(
        case_context='Contract breach dispute',
        jurisdiction='India',
        case_type='civil',
        user_constraints={},
    )

    assert isinstance(result, dict)
    assert 'status' in result
    assert 'issues' in result
    assert 'precedents' in result
