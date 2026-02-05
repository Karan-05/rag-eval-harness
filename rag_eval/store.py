import json
import sqlite3
from hashlib import sha256
from pathlib import Path
from typing import Iterable

import numpy as np


def embed_text(text: str) -> np.ndarray:
	digest = sha256(text.encode("utf-8")).digest()
	vector = np.frombuffer(digest, dtype=np.uint8).astype(np.float32)
	vector = vector[:32]
	return vector / (np.linalg.norm(vector) + 1e-9)


class VectorStore:
	def __init__(self, path: Path):
		self.path = Path(path)
		self.conn = sqlite3.connect(self.path)
		self._init()

	def _init(self) -> None:
		self.conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS documents (
				id TEXT PRIMARY KEY,
				text TEXT NOT NULL,
				embedding TEXT NOT NULL
			)
			""",
		)
		self.conn.commit()

	def upsert(self, doc_id: str, text: str) -> None:
		embedding = embed_text(text).tolist()
		self.conn.execute(
			"REPLACE INTO documents (id, text, embedding) VALUES (?, ?, ?)",
			(doc_id, text, json.dumps(embedding)),
		)
		self.conn.commit()

	def bulk_load(self, documents: Iterable[tuple[str, str]]) -> None:
		for doc_id, text in documents:
			self.upsert(doc_id, text)

	def search(self, query: str, k: int = 3) -> list[tuple[str, float]]:
		q_emb = embed_text(query)
		results = []
		for doc_id, text, raw_emb in self.conn.execute("SELECT id, text, embedding FROM documents"):
			emb = np.array(json.loads(raw_emb), dtype=np.float32)
			score = float(np.dot(q_emb, emb))
			results.append((doc_id, score, text))
		results.sort(key=lambda item: item[1], reverse=True)
		return [(doc_id, score) for doc_id, score, _ in results[:k]]

	def close(self) -> None:
		self.conn.close()
