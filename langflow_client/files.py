from __future__ import annotations

from typing import Any, Dict, List, Optional

from .user_file import UserFile


class Files:
    def __init__(self, client):
        self.client = client

    def upload(self, file_obj, *, filename: Optional[str] = None, content_type: Optional[str] = None, signal: Optional[Any] = None) -> UserFile:
        files = {"file": (filename or getattr(file_obj, "name", "file"), file_obj, content_type or "application/octet-stream")}
        headers = {"Accept": "application/json"}
        response = self.client.request(
            path="/v2/files",
            method="POST",
            body=files,
            headers=headers,
            signal=signal,
        )
        return UserFile(response)

    def list(self, *, signal: Optional[Any] = None) -> List[UserFile]:
        headers = {"Accept": "application/json"}
        response = self.client.request(
            path="/v2/files",
            method="GET",
            headers=headers,
            signal=signal,
        )
        return [UserFile(item) for item in response] 