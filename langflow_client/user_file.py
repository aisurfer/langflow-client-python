from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserFile:
    id: str
    name: str
    path: str
    size: int
    provider: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __init__(self, data: dict):
        self.id = data.get("id")
        self.name = data.get("name")
        self.path = data.get("path")
        self.size = data.get("size")
        self.provider = data.get("provider")
        self.user_id = data.get("user_id")
        created_at = data.get("created_at")
        updated_at = data.get("updated_at")
        self.created_at = (
            datetime.fromisoformat(created_at.replace("Z", "+00:00")) if isinstance(created_at, str) else None
        )
        self.updated_at = (
            datetime.fromisoformat(updated_at.replace("Z", "+00:00")) if isinstance(updated_at, str) else None
        ) 