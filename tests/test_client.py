from unittest.mock import MagicMock

import pytest

from langflow_client.client import LangflowClient
from langflow_client.errors import LangflowError, LangflowRequestError
from langflow_client.flow import Flow


class DummyResponse:
    def __init__(self, json_data=None, *, ok=True, status=200, reason="OK"):
        self._json = json_data
        self.ok = ok
        self.status_code = status
        self.reason = reason

    def json(self):
        return self._json


def test_client_init_requires_base_url():
    with pytest.raises(TypeError):
        LangflowClient({})
    with pytest.raises(TypeError):
        LangflowClient({"base_url": ""})
    with pytest.raises(TypeError):
        LangflowClient({"base_url": None})


def test_custom_url_init_and_path():
    client = LangflowClient({"base_url": "http://localhost:1234"})
    assert client.base_url == "http://localhost:1234"
    assert client.base_path == "/api"


def test_request_success_and_auth_header():
    session = MagicMock()
    session.request.return_value = DummyResponse({"session_id": "sid", "outputs": []})
    client = LangflowClient({"base_url": "http://localhost:1234", "api_key": "k", "session": session})
    client.request(path=f"/v1/run/flow-id", method="POST", headers={})
    _, kwargs = session.request.call_args
    headers = kwargs["headers"]
    assert headers.get("x-api-key") == "k"


def test_request_error_status():
    session = MagicMock()
    session.request.return_value = DummyResponse({}, ok=False, status=401, reason="Unauthorized")
    client = LangflowClient({"base_url": "http://localhost:1234", "session": session})
    with pytest.raises(LangflowError) as exc:
        client.request(path=f"/v1/run/flow-id", method="POST", headers={})
    assert "401 - Unauthorized" in str(exc.value)


def test_request_transport_error():
    session = MagicMock()
    session.request.side_effect = RuntimeError("Internal Server Error")
    client = LangflowClient({"base_url": "http://localhost:1234", "session": session})
    with pytest.raises(LangflowRequestError):
        client.request(path=f"/v1/run/flow-id", method="POST", headers={})


def test_flow_factory():
    client = LangflowClient({"base_url": "http://localhost:1234"})
    flow = client.flow("flow-id")
    assert isinstance(flow, Flow)
    assert flow.id == "flow-id" 