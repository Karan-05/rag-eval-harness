from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class EvalSettings(BaseSettings):
	dataset_path: Path = Path("data/questions.jsonl")
	cache_path: Path = Path(".cache/evals.sqlite")
	store_path: Path = Path("data/embeddings.sqlite")
	top_k: int = 3
	metric: Literal["hit_rate"] = "hit_rate"

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class EvalResult(BaseModel):
	question_id: str
	retrieved_ids: list[str]
	latency_ms: float
	hit: bool
