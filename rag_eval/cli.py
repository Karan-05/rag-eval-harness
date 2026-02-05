import asyncio
from typing import Optional

import typer

from .config import EvalSettings
from .evaluator import Evaluator
from .store import VectorStore
from .data import load_questions

app = typer.Typer(help="RAG evaluation harness CLI")


@app.command()
def ingest(dataset: Optional[str] = typer.Option(None, help="Path to dataset JSONL")):
	settings = EvalSettings()
	if dataset:
		settings.dataset_path = dataset
	store = VectorStore(settings.store_path)
	store.bulk_load((item["id"], item["context"]) for item in load_questions(settings.dataset_path))
	store.close()
	typer.echo(f"Ingested documents into {settings.store_path}")


@app.command()
def evaluate(async_mode: bool = typer.Option(False, "--async", help="Run with async workers"), use_cache: bool = True):
	settings = EvalSettings()
	runner = Evaluator(settings)
	try:
		if async_mode:
			summary = asyncio.run(runner.run_async(use_cache=use_cache))
		else:
			summary = runner.run(use_cache=use_cache)
	finally:
		runner.close()
	typer.echo(summary)


if __name__ == "__main__":
	app()
