import pytest

from app.research.embeddings import EmbeddingProvider, HashEmbeddingProvider


def test_hash_embedding_provider_is_embedding_provider():
    provider = HashEmbeddingProvider()

    assert isinstance(provider, EmbeddingProvider)
    assert provider.dimension == 256


def test_embedding_is_deterministic():
    provider = HashEmbeddingProvider(dimension=64)

    first = provider.embed("Revenue increased during the fiscal year.")
    second = provider.embed("Revenue increased during the fiscal year.")

    assert first == second


def test_embedding_has_expected_dimension():
    provider = HashEmbeddingProvider(dimension=128)

    embedding = provider.embed("Risk factors may affect future results.")

    assert len(embedding) == 128


def test_embedding_is_normalized():
    provider = HashEmbeddingProvider(dimension=128)

    embedding = provider.embed("Operating income increased.")

    norm = sum(value * value for value in embedding) ** 0.5

    assert norm == pytest.approx(1.0)


def test_similar_text_has_nonzero_similarity():
    provider = HashEmbeddingProvider(dimension=256)

    first = provider.embed("Revenue increased significantly during the year.")
    second = provider.embed("Revenue increased during the fiscal year.")

    similarity = sum(a * b for a, b in zip(first, second, strict=True))

    assert similarity > 0


def test_different_text_produces_embedding():
    provider = HashEmbeddingProvider(dimension=128)

    first = provider.embed("Revenue increased.")
    second = provider.embed("Litigation risk increased.")

    assert first != second


def test_empty_text_is_rejected():
    provider = HashEmbeddingProvider()

    with pytest.raises(ValueError, match="Text cannot be empty"):
        provider.embed("")


def test_embed_many_preserves_order():
    provider = HashEmbeddingProvider(dimension=64)

    texts = [
        "Revenue increased.",
        "Operating expenses decreased.",
        "Cash flow remained strong.",
    ]

    embeddings = provider.embed_many(texts)

    assert len(embeddings) == len(texts)
    assert embeddings[0] == provider.embed(texts[0])
    assert embeddings[1] == provider.embed(texts[1])
    assert embeddings[2] == provider.embed(texts[2])
