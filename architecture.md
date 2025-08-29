# langflow_client Architecture

- **Package name**: `langflow_client` (importable as `import langflow_client`)
- **Distribution name**: `langflow-client`
- **License**: Apache-2.0 (same as reference client)

## Modules

- `langflow_client/__init__.py`
  - Public API surface: exports `LangflowClient`, `Flow`, `FlowResponse`, `Files`, `UserFile`, `Log`, constants `InputTypes`, `OutputTypes`, and errors `LangflowError`, `LangflowRequestError`.

- `langflow_client/consts.py`
  - `InputTypes` and `OutputTypes` string enums for input/output typing.

- `langflow_client/errors.py`
  - `LangflowError(Exception)`: wraps non-OK HTTP responses; stores `cause` (the response object)
  - `LangflowRequestError(Exception)`: wraps request transport errors; stores `cause` (the original error)

- `langflow_client/ndjson.py`
  - `iter_ndjson_objects(chunk_iter)`: tolerant NDJSON parser over byte/text chunks, buffering partial JSON and yielding parsed objects as soon as they are complete.

- `langflow_client/log.py`
  - `Log` dataclass: `timestamp: datetime`, `message: str`.

- `langflow_client/logs.py`
  - `Logs` helper bound to a `LangflowClient` to fetch and stream logs.
    - `fetch(options)` → list[`Log`]
    - `stream(options)` → iterator over `Log` parsed from NDJSON of `{timestamp: message}` maps.

- `langflow_client/user_file.py`
  - `UserFile` dataclass mapping v2 upload API response; parses `created_at`/`updated_at` to `datetime` if provided.

- `langflow_client/flow_response.py`
  - `FlowResponse` wraps the flow run result with `.session_id`, `.outputs`, and convenience `.chat_output_text()` that mirrors TS `chatOutputText()` logic.

- `langflow_client/files.py`
  - `Files` helper bound to a `LangflowClient` to call v2 file APIs:
    - `upload(file, *, filename=None, content_type=None, signal=None)` → `UserFile`
    - `list(signal=None)` → list[`UserFile`]

- `langflow_client/flow.py`
  - `Flow` represents a flow with optional tweaks; immutable `.tweak(key, tweak)` returns new `Flow` instance; supports:
    - `run(input_value, *, input_type="chat", output_type="chat", session_id=None, tweaks=None, signal=None)` → `FlowResponse`
    - `stream(input_value, ...)` → iterator over stream events (NDJSON)
    - `upload_file(file, *, filename=None, content_type=None, signal=None)` → `UploadResponse`

- `langflow_client/client.py`
  - `LangflowClient` core HTTP client:
    - Constructor takes base URL and optional API key
    - `request(path, method, *, query=None, body=None, headers=None, signal=None)` → JSON
    - `stream(path, method, *, body=None, headers=None, signal=None)` → iterator over parsed NDJSON objects
    - Exposes `.flow(id, tweaks=None)`, `.logs`, `.files` helpers.

- `langflow_client/types.py` (lightweight types)
  - Python typing aliases to mirror TS types (e.g., `Tweaks`, `Tweak`, `StreamEvent` protocol types) to aid static analysis.

## HTTP & Streaming

- Uses `requests` under the hood by default.
- Allows dependency injection of a custom `fetch` callable for testing (mimicking TS `fetch` override). The callable should return a minimal response object with `.ok`, `.status_code`, `.reason`, `.json()`, `.text`, and optional `.iter_content()` for streaming.
- Streaming endpoints (`/v1/run/{id}?stream=true`, `/logs-stream`) are parsed via `iter_ndjson_objects` to yield events as Python dicts or `Log` objects.

## URL & Headers behavior

- Base URL is required and must be provided during client initialization
- API key is optional and when provided is sent via the `x-api-key` header
- `User-Agent` header set if absent: `langflow-client-python/{version} ({platform} {arch}) python/{version}`.

## Testing

- Pytest test suite mirrors TS coverage:
  - `test_client.py`, `test_flow.py`, `test_flow_response.py`, `test_ndjson.py`, `test_logs.py`, `test_files.py`, `test_user_file.py`.
  - Utilities to create a mock `fetch` callable and to compare binary blobs.
  - JSON fixtures reused from TS reference for parity.

## Packaging & Tooling

- `pyproject.toml` with project metadata, Apache-2.0 license, `requests` runtime dependency, and `pytest` as dev-dependency.
- `uv`-based workflow for local venv, install, lint/test.

## Public API (import surface)

```python
from langflow_client import (
    LangflowClient, Flow, FlowResponse, Files, UserFile, Log,
    InputTypes, OutputTypes, LangflowError, LangflowRequestError,
)
``` 