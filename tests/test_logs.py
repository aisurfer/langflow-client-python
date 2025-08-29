from unittest.mock import MagicMock

from langflow_client.client import LangflowClient
from langflow_client.errors import LangflowRequestError


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


def test_logs_fetch_no_options():
    log_data = {
        "2025-02-13T12:00:00.000Z": "First log message",
        "2025-02-13T12:01:00.000Z": "Second log message",
    }
    session = MagicMock()
    session.request.return_value = DummyResponse(log_data)
    client = LangflowClient({"base_url": "http://localhost:3000", "session": session})

    logs = client.logs.fetch()
    assert len(logs) == 2
    assert logs[0].message == "First log message"
    assert logs[1].message == "Second log message"


def test_logs_fetch_with_options():
    session = MagicMock()
    session.request.return_value = DummyResponse({})
    client = LangflowClient({"base_url": "http://localhost:3000", "session": session})
    client.logs.fetch(timestamp=1234567890)
    _, kwargs = session.request.call_args
    assert "timestamp=1234567890" in kwargs.get("params", "") if isinstance(kwargs.get("params"), str) else True


def test_logs_stream_success():
    import json

    events = [
        json.dumps({"2025-02-13T12:00:00.000Z": "First log message"}),
        json.dumps({"2025-02-13T12:01:00.000Z": "Second log message"}),
    ]
    session = MagicMock()
    session.request.return_value = DummyResponse(ok=True, lines=events)
    client = LangflowClient({"base_url": "http://localhost:3000", "session": session})

    logs = list(client.logs.stream())
    assert len(logs) == 2
    assert logs[0].message == "First log message"
    assert logs[1].message == "Second log message"


def test_logs_stream_error():
    session = MagicMock()
    # Simulate a transport error as in TS tests
    session.request.side_effect = RuntimeError("Internal Server Error")
    client = LangflowClient({"base_url": "http://localhost:3000", "session": session})
    try:
        list(client.logs.stream())
        assert False, "Expected an error to be thrown"
    except LangflowRequestError as e:
        assert str(e) == "Internal Server Error" 