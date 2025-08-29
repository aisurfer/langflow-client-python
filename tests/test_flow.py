from io import BytesIO
from unittest.mock import MagicMock

from langflow_client.client import LangflowClient
from langflow_client.flow import Flow
from langflow_client.flow_response import FlowResponse
from langflow_client.upload_response import UploadResponse


class DummyResponse:
    def __init__(self, json_data=None, *, ok=True, status=200, reason="OK", lines=None):
        self._json = json_data
        self.ok = ok
        self.status_code = status
        self.reason = reason
        self._lines = lines or []

    def json(self):
        return self._json

    def iter_lines(self, decode_unicode=False):
        for l in self._lines:
            yield l


def make_client(resp):
    session = MagicMock()
    session.request.return_value = resp
    client = LangflowClient({"base_url": "http://localhost:7860", "session": session})
    return client, session


def test_flow_init_and_tweak():
    client = LangflowClient({"base_url": "http://localhost:7860"})
    flow = Flow(client, "flow-id")
    assert flow.client is client
    assert flow.id == "flow-id"
    tweaked = flow.tweak("key", {"k": "v"})
    assert tweaked is not flow
    assert tweaked.tweaks == {"key": {"k": "v"}}


def test_flow_run_posts_to_endpoint():
    client, session = make_client(DummyResponse({"session_id": "sid", "outputs": []}))
    flow = Flow(client, "flow-id")
    result = flow.run("Hello")
    assert isinstance(result, FlowResponse)
    args, kwargs = session.request.call_args
    assert args[0] == "POST"
    assert args[1].endswith("/api/v1/run/flow-id")


def test_flow_run_with_options():
    client, session = make_client(DummyResponse({"session_id": "sid", "outputs": []}))
    flow = Flow(client, "flow-id")
    result = flow.run("Hello", input_type="chat", output_type="chat")
    assert isinstance(result, FlowResponse)


def test_flow_stream_makes_streaming_request():
    import json

    events = [
        json.dumps({"event": "add_message", "data": {}}),
        json.dumps({"event": "token", "data": {"id": "abc123", "chunk": "Hello", "timestamp": "ts"}}),
        json.dumps({"event": "end", "data": {"result": {"session_id": "def465", "outputs": []}}}),
    ]
    client, session = make_client(DummyResponse(ok=True, lines=events))
    flow = Flow(client, "flow-id")
    stream = flow.stream("Hello")
    events = list(stream)
    assert len(events) == 3


def test_flow_upload_file():
    client, session = make_client(DummyResponse({"flowId": "flow-id", "file_path": "folder/date-file.jpg"}))
    flow = Flow(client, "flow-id")
    result = flow.upload_file(BytesIO(b"abc"), filename="bodi.jpg", content_type="image/jpeg")
    assert isinstance(result, UploadResponse)
    assert result.flow_id == "flow-id" 