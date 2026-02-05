from pathlib import Path

from rag_eval.store import VectorStore


def test_vector_store_returns_best_match(tmp_path):
	store_path = tmp_path / "store.sqlite"
	store = VectorStore(store_path)
	store.upsert("doc1", "38% lower inference cost via caching")
	store.upsert("doc2", "60fps UI at 100k rows by windowing")

	results = store.search("38% lower inference cost via caching", k=1)
	assert results[0][0] == "doc1"
	store.close()
