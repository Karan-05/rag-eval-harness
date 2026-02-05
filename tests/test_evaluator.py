from rag_eval.config import EvalSettings
from rag_eval.evaluator import Evaluator


def test_evaluator_computes_hit_rate(tmp_path):
	settings = EvalSettings(
		dataset_path="data/questions.jsonl",
		cache_path=tmp_path / "cache.sqlite",
		store_path=tmp_path / "store.sqlite",
		top_k=2,
	)
	evaluator = Evaluator(settings)
	try:
		summary = evaluator.run(use_cache=False)
		assert summary["samples"] == 3
		assert 0 <= summary["hit_rate"] <= 1
	finally:
		evaluator.close()
