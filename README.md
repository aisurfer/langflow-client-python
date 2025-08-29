# Python client for the Langflow API

This package provides an easy way to use the Langflow API to run flows from Python applications.

- **Package**: `langflow-client`
- **Import**: `import langflow_client`
- **License**: Apache-2.0

## Installation

Using uv (recommended):

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Using pip:

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Prerequisites

- Base URL of your Langflow instance
- API key if authentication is enabled on your instance

## Usage

### Initialization

```python
from langflow_client import LangflowClient

client = LangflowClient({
    "base_url": "http://localhost:7860",
    "api_key": "sk-...",  # optional
})
```

### Running a flow

```python
flow = client.flow("<flow-id>")
response = flow.run("Hello, world!")
print(response.outputs)
print(response.chat_output_text())
```

You can pass tweaks and IO options:

```python
from langflow_client.consts import InputTypes, OutputTypes

response = flow.run(
    "Hello",
    input_type=InputTypes.CHAT,
    output_type=OutputTypes.CHAT,
    session_id="optional-session-id",
    tweaks={"ChatInput-abc": {"temperature": 0.2}},
)
```

### Streaming

```python
for event in flow.stream("Hello"):
    print(event)
```

Events are dicts with `event` keys such as `add_message`, `token`, and `end`.

### File upload

- v1 flow-scoped image upload:

```python
with open("image.jpg", "rb") as f:
    upload = flow.upload_file(f, filename="image.jpg", content_type="image/jpeg")
    print(upload.file_path)
```

- v2 user-scoped file upload and listing:

```python
with open("document.pdf", "rb") as f:
    uploaded = client.files.upload(f, filename="document.pdf", content_type="application/pdf")

files = client.files.list()
```

### Logs

```python
# Fetch recent logs
logs = client.logs.fetch()

# Stream logs
for log in client.logs.stream():
    print(log.timestamp, log.message)
```

### Aborting requests

Pass a custom object with `throw_if_aborted()` to emulate AbortController semantics if desired. Alternatively, use request timeouts at the HTTP layer.

## Development

- Create env and install dev dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
uv pip install pytest ruff
```

- Run tests:

```bash
pytest
```

- Lint:

```bash
ruff check .
```

## Publishing to PyPI

1. Update version in `pyproject.toml`.
2. Build:

```bash
python -m build
```

3. Upload:

```bash
python -m twine upload dist/*
```

## License

Apache License 2.0. See `LICENSE`