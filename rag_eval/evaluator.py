import asyncio
from time import perf_counter
from typing import Iterable

from .cache import EvalCache
from .config import EvalResult, EvalSettings
from .data import load_questions
from .store import VectorStore


class Evaluator:
	def __init__(self, settings: EvalSettings | None = None):
		self.settings = settings or EvalSettings()
		self.store = VectorStore(self.settings.store_path)
		self.cache = EvalCache(self.settings.cache_path)

	def seed_store(self) -> None:
		docs = (
			(item["id"], item["context"])
			for item in load_questions(self.settings.dataset_path)
		)
		self.store.bulk_load(docs)

	def _evaluate_question(self, question: dict, use_cache: bool = True) -> EvalResult:
		cached = self.cache.get(question["id"]) if use_cache else None
		if cached:
			return EvalResult(**cached)

		start = perf_counter()
		retrieved = self.store.search(question["question"], self.settings.top_k)
		latency = (perf_counter() - start) * 1000
		retrieved_ids = [doc_id for doc_id, _ in retrieved]
		hit = question["id"] in retrieved_ids

		result = EvalResult(
			question_id=question["id"],
			retrieved_ids=retrieved_ids,
			latency_ms=latency,
			hit=hit,
		)
		self.cache.set(question["id"], result.model_dump())
		return result

	def run(self, use_cache: bool = True) -> dict:
		self.seed_store()
		results = [
			self._evaluate_question(q, use_cache=use_cache)
			for q in load_questions(self.settings.dataset_path)
		]
		return self._summaries(results)

	async def run_async(self, use_cache: bool = True) -> dict:
		self.seed_store()
		semaphore = asyncio.Semaphore(5)

		async def evaluate_entry(entry: dict):
			async with semaphore:
				return self._evaluate_question(entry, use_cache=use_cache)

		results = await asyncio.gather(
			*[evaluate_entry(q) for q in load_questions(self.settings.dataset_path)],
		)
		return self._summaries(results)

	def _summaries(self, results: Iterable[EvalResult]) -> dict:
		results = list(results)
		total = len(results)
		hits = sum(1 for r in results if r.hit)
		latency = sum(r.latency_ms for r in results) / total if total else 0
		return {
			"samples": total,
			"hit_rate": hits / total if total else 0,
			"avg_latency_ms": latency,
			"results": [r.model_dump() for r in results],
		}

	def close(self) -> None:
		self.store.close()
		self.cache.close()
