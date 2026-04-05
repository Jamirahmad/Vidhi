from backend.app.main import compact_content_excerpt, extract_source_fields, is_provision_candidate


def test_extract_source_fields_uses_fallback_url() -> None:
    content = """
    Source: Supreme Court of India
    Reference URL: 
    """

    result = extract_source_fields(content, fallback_url="https://example.org/fallback")

    assert result["sourceName"] == "Supreme Court of India"
    assert result["sourceUrl"] == "https://example.org/fallback"


def test_is_provision_candidate_detects_keywords() -> None:
    item = {
        "title": "Section 138 NI Act",
        "summary": "Dishonour of cheque",
        "content": "Text discussing section and act context",
    }

    assert is_provision_candidate(item) is True


def test_is_provision_candidate_rejects_non_legal_text() -> None:
    item = {
        "title": "General note",
        "summary": "A generic summary",
        "content": "No statutory markers present",
    }

    assert is_provision_candidate(item) is False


def test_compact_content_excerpt_truncates_with_ellipsis() -> None:
    long_text = "word " * 500

    excerpt = compact_content_excerpt(long_text, limit_chars=120)

    assert len(excerpt) <= 123
    assert excerpt.endswith("...")
