# Contributing

## Dev setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

## Useful commands

- `python -m rag_eval.cli ingest` – load new datasets (JSONL).
- `python -m rag_eval.cli evaluate --async` – run async evaluation loop.
- `uvicorn rag_eval.api:app --reload` – REST surface.

## Tests

```
ruff check rag_eval
pytest
```

Update the dataset, store format, or metrics? Add unit tests alongside to keep coverage meaningful.
