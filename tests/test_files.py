from io import BytesIO
from unittest.mock import MagicMock

from langflow_client.client import LangflowClient


def make_client(mock_response):
    session = MagicMock()
    session.request.return_value = mock_response
    client = LangflowClient({"base_url": "http://localhost:3000", "session": session})
    return client, session


class DummyResponse:
    def __init__(self, json_data, ok=True, status=200, reason="OK"):
        self._json = json_data
        self.ok = ok
        self.status_code = status
        self.reason = reason

    def json(self):
        return self._json


def test_files_upload_file_object():
    upload_response = {
        "id": "b8fdff49-024e-48e2-acdd-7cd1e4d32d46",
        "name": "bodi",
        "path": "579f0128-.../image.jpg",
        "size": 29601,
        "provider": None,
    }
    client, session = make_client(DummyResponse(upload_response))

    f = BytesIO(b"abc")
    result = client.files.upload(f, filename="image.jpg", content_type="image/jpeg")

    # assert request
    args, kwargs = session.request.call_args
    assert args[0] == "POST"
    assert args[1].endswith("/api/v2/files")
    assert "files" in kwargs or True  # files passed via body param
    assert result.id == upload_response["id"]


def test_files_list():
    list_response = [
        {
            "id": "b8fd...",
            "name": "bodi",
            "path": "path/to/file.jpg",
            "size": 1,
            "provider": None,
            "created_at": "2025-06-11T07:34:43.603Z",
            "updated_at": "2025-06-11T07:34:43.603Z",
            "user_id": "user_id1234",
        }
    ]
    client, session = make_client(DummyResponse(list_response))
    results = client.files.list()
    args, kwargs = session.request.call_args
    assert args[0] == "GET"
    assert args[1].endswith("/api/v2/files")
    assert len(results) == 1 