from __future__ import annotations

from typing import Dict, Iterator, List, Optional

from .log import Log


class Logs:
    def __init__(self, client):
        self.client = client

    def fetch(self, *, timestamp: Optional[int] = None, lines_before: Optional[int] = None, lines_after: Optional[int] = None, signal=None) -> List[Log]:
        query: Dict[str, str] = {}
        if timestamp is not None:
            query["timestamp"] = str(timestamp)
        if lines_before is not None:
            query["lines_before"] = str(lines_before)
        if lines_after is not None:
            query["lines_after"] = str(lines_after)
        headers = {"Accept": "application/json"}
        response = self.client.request(
            path="/logs",
            method="GET",
            headers=headers,
            query=query or None,
            signal=signal,
        )
        return sorted(
            [Log(ts, msg) for ts, msg in response.items()],
            key=lambda l: l.timestamp,
        )

    def stream(self, *, signal=None) -> Iterator[Log]:
        headers = {"Accept": "text/event-stream"}
        stream = self.client.stream(
            path="/logs-stream",
            method="GET",
            headers=headers,
            signal=signal,
        )
        for chunk in stream:
            for ts, msg in chunk.items():
                yield Log(ts, msg) 