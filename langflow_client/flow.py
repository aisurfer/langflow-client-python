from __future__ import annotations

from typing import Any, Dict, Iterator, Mapping, Optional

from .flow_response import FlowResponse


class Flow:
    def __init__(self, client, flow_id: str, tweaks: Optional[Dict[str, Any]] = None):
        self.client = client
        self.id = flow_id
        self.tweaks: Dict[str, Any] = tweaks or {}

    def tweak(self, key: str, tweak: Mapping[str, Any] | str):
        new_tweaks = dict(self.tweaks)
        new_tweaks[key] = tweak
        return Flow(self.client, self.id, new_tweaks)

    def run(
        self,
        input_value: str,
        *,
        input_type: str = "chat",
        output_type: str = "chat",
        session_id: Optional[str] = None,
        tweaks: Optional[Dict[str, Any]] = None,
        signal: Optional[Any] = None,
    ) -> FlowResponse:
        final_tweaks = {**self.tweaks, **(tweaks or {})}
        payload = {
            "input_type": input_type,
            "output_type": output_type,
            "input_value": input_value,
            "tweaks": final_tweaks,
            "session_id": session_id,
        }
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        result = self.client.request(
            path=f"/v1/run/{self.id}",
            method="POST",
            body=__import__("json").dumps(payload),
            headers=headers,
            signal=signal,
        )
        return FlowResponse(result)

    def stream(
        self,
        input_value: str,
        *,
        input_type: str = "chat",
        output_type: str = "chat",
        session_id: Optional[str] = None,
        tweaks: Optional[Dict[str, Any]] = None,
        signal: Optional[Any] = None,
    ) -> Iterator[dict]:
        final_tweaks = {**self.tweaks, **(tweaks or {})}
        payload = {
            "input_type": input_type,
            "output_type": output_type,
            "input_value": input_value,
            "tweaks": final_tweaks,
            "session_id": session_id,
        }
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        return self.client.stream(
            path=f"/v1/run/{self.id}",
            method="POST",
            body=__import__("json").dumps(payload),
            headers=headers,
            signal=signal,
        )

    def upload_file(self, file_obj, *, filename: Optional[str] = None, content_type: Optional[str] = None, signal: Optional[Any] = None):
        from .upload_response import UploadResponse

        files = {"file": (filename or getattr(file_obj, "name", "file"), file_obj, content_type or "application/octet-stream")}
        headers = {"Accept": "application/json"}
        response = self.client.request(
            path=f"/v1/files/upload/{self.id}",
            method="POST",
            body=files,
            headers=headers,
            signal=signal,
        )
        return UploadResponse(response) 