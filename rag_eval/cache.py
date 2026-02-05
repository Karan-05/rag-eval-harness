import json
import sqlite3
from pathlib import Path
from typing import Optional


class EvalCache:
	def __init__(self, path: Path):
		self.path = Path(path)
		self.path.parent.mkdir(parents=True, exist_ok=True)
		self.conn = sqlite3.connect(self.path)
		self._init()

	def _init(self) -> None:
		self.conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS eval_cache (
				question_id TEXT PRIMARY KEY,
				payload TEXT NOT NULL
			)
			""",
		)
		self.conn.commit()

	def get(self, question_id: str) -> Optional[dict]:
		row = self.conn.execute(
			"SELECT payload FROM eval_cache WHERE question_id = ?", (question_id,),
		).fetchone()
		if not row:
			return None
		return json.loads(row[0])

	def set(self, question_id: str, payload: dict) -> None:
		self.conn.execute(
			"REPLACE INTO eval_cache (question_id, payload) VALUES (?, ?)",
			(question_id, json.dumps(payload)),
		)
		self.conn.commit()

	def close(self) -> None:
		self.conn.close()
