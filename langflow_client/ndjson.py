from __future__ import annotations

from typing import Iterable, Iterator


def iter_ndjson_objects(chunks: Iterable[bytes | str]) -> Iterator[dict]:
    buffer = ""
    for chunk in chunks:
        text = chunk.decode("utf-8", errors="ignore") if isinstance(chunk, (bytes, bytearray)) else str(chunk)
        lines = text.split("\n")
        for line in lines:
            if len(buffer) == 0:
                if line.lstrip().startswith("{"):
                    buffer += line
            else:
                buffer += line
            try:
                if buffer:
                    obj = __import__("json").loads(buffer)
                    yield obj
                    buffer = ""
            except Exception:
                # keep buffering until valid JSON
                pass 