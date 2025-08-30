# Langflow Client Integration Tests

These integration tests serve both as test cases and as examples of how to use the Langflow client library. Each test file focuses on a specific aspect of the client's functionality and includes detailed comments explaining the usage.

## Prerequisites

- Python 3.7+
- Langflow server running (default: http://localhost:7860)
- API key for authentication
- Test flow ID (a simple echo flow that returns "Your request is: {input}")
- Test dependencies (install with `pip install langflow-client[test]`)

## Environment Setup

Create a `.env` file in the project root with the following variables:

```bash
LANGFLOW_SERVER_URL=http://localhost:7860
LANGFLOW_API_KEY=your-api-key
LANGFLOW_FLOW_ID=your-flow-id
```

The tests will automatically load these environment variables using python-dotenv. If any required variables are missing, the tests will fail with a helpful error message.

## Test Structure

### Basic Operations
- `test_flow_operations.py`: Examples of running flows, streaming responses, and using tweaks
- `test_file_operations.py`: Examples of file upload, listing, and management
- `test_log_operations.py`: Examples of fetching and streaming logs (currently skipped)

### Advanced Operations
- `test_advanced_operations.py`: Examples of:
  - Concurrent flow operations
  - Large file handling
  - Binary file uploads
  - Error recovery scenarios
  - Async operations

## Running the Tests

1. Ensure Langflow server is running:
   ```bash
   docker ps | grep langflow
   ```

2. Install test dependencies:
   ```bash
   # If installing from source
   pip install -e ".[test]"
   
   # If installing from PyPI
   pip install "langflow-client[test]"
   ```

3. Create and configure your `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. Run the tests:
   ```bash
   # Run all tests
   pytest integration_tests/

   # Run specific test file
   pytest integration_tests/test_flow_operations.py

   # Run with verbose output
   pytest -v integration_tests/

   # Run without skipped tests
   pytest -v integration_tests/ -k "not skip"
   ```

## Example Usage

### Basic Flow Operation
```python
from langflow_client import LangflowClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize client
client = LangflowClient({
    "base_url": os.getenv("LANGFLOW_SERVER_URL"),
    "api_key": os.getenv("LANGFLOW_API_KEY")
})

# Get a flow
flow = client.flow(os.getenv("LANGFLOW_FLOW_ID"))

# Run the flow
response = flow.run("Hello, Langflow!")
print(response.chat_output_text())
```

### Concurrent Operations
```python
import concurrent.futures

# Run multiple flows concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(flow.run, f"Request {i}")
        for i in range(4)
    ]
    responses = [future.result() for future in futures]
```

### File Operations
```python
# Upload a file
with open("large_file.txt", "rb") as f:
    response = client.files.upload(
        f,
        filename="large_file.txt",
        content_type="text/plain"
    )

# List files
files = client.files.list()

# Delete a file
client.files.delete(response.id)
```

See individual test files for more examples of specific features. 