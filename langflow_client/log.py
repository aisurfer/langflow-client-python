from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Log:
    timestamp: datetime
    message: str

    def __init__(self, timestamp: str, message: str):
        # TS parses from integer milliseconds string; tests pass ISO strings.
        try:
            if timestamp.isdigit():
                self.timestamp = datetime.fromtimestamp(int(timestamp) / 1000)
            else:
                # ISO 8601
                self.timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except Exception:
            self.timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        self.message = message 