import json
from pathlib import Path
from typing import Iterator


def load_questions(path: Path) -> Iterator[dict]:
	with Path(path).open() as handle:
		for line in handle:
			line = line.strip()
			if not line:
				continue
			yield json.loads(line)
