from backend.app.knowledge.embeddings import HashEmbeddings


def test_hash_embeddings_caches_repeat_queries() -> None:
    embeddings = HashEmbeddings(dimensions=128)

    first = embeddings.embed_query("Section 420 IPC")
    second = embeddings.embed_query("Section 420 IPC")

    assert first == second
    assert len(embeddings._cache) == 1  # noqa: SLF001 - cache behavior verification


def test_hash_embeddings_cache_eviction_respects_limit(monkeypatch) -> None:
    monkeypatch.setenv("VIDHI_EMBED_CACHE_MAX_ENTRIES", "128")
    embeddings = HashEmbeddings(dimensions=128)

    for idx in range(140):
        embeddings.embed_query(f"query-{idx}")

    assert len(embeddings._cache) <= 128  # noqa: SLF001 - cache behavior verification
