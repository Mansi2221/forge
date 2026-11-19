from app.rag.pipeline import VectorStore, chunk_text, generate_embedding, ingest_document, vector_store


def test_chunk_text():
    text = " ".join([f"word{i}" for i in range(100)])
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 20 for c in chunks)


def test_generate_embedding():
    emb = generate_embedding("hello world")
    assert len(emb) == 64
    norm = sum(x * x for x in emb) ** 0.5
    assert abs(norm - 1.0) < 0.01


def test_vector_store_add_and_search():
    store = VectorStore()
    emb1 = generate_embedding("machine learning")
    emb2 = generate_embedding("deep learning")
    emb3 = generate_embedding("cooking recipes")

    store.add("1", "machine learning", emb1, {})
    store.add("2", "deep learning", emb2, {})
    store.add("3", "cooking recipes", emb3, {})

    query_emb = generate_embedding("neural networks")
    results = store.search(query_emb, top_k=2)
    assert len(results) == 2


def test_ingest_document():
    vector_store.clear()
    text = " ".join([f"sentence{i} about AI and machine learning" for i in range(50)])
    count = ingest_document("test.txt", text)
    assert count > 0
    assert vector_store.count == count
    vector_store.clear()
