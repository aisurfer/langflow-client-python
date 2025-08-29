from __future__ import annotations

from typing import Any, List


class FlowResponse:
    def __init__(self, response: dict):
        # The TS fixtures sometimes use sessionId (camel) in fixtures, but actual API uses session_id
        self.session_id: str = response.get("session_id") or response.get("sessionId")
        self.outputs: List[dict] = response.get("outputs", [])

    def chat_output_text(self) -> str | None:
        for outputs in self.outputs:
            outputs_list = outputs.get("outputs")
            if isinstance(outputs_list, list):
                chat_output = next(
                    (o for o in outputs_list if o and o.get("outputs", {}).get("message")),
                    None,
                )
                if chat_output:
                    container = chat_output.get("outputs", {}).get("message")
                    if isinstance(container, str):
                        return container
                    if isinstance(container, dict):
                        inner = container.get("message")
                        if isinstance(inner, str):
                            return inner
                        if isinstance(inner, dict):
                            text = inner.get("text")
                            if isinstance(text, str):
                                return text
                        text = container.get("text")
                        if isinstance(text, str):
                            return text
        return None 