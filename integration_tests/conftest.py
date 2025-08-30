import os
import pytest
import shutil
import uuid
from pathlib import Path
from dotenv import load_dotenv
from langflow_client import LangflowClient

# Load environment variables from .env file
load_dotenv()

# Test environment configuration
LANGFLOW_SERVER_URL = os.getenv("LANGFLOW_SERVER_URL")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY")
TEST_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID")

# Validate required environment variables
if not all([LANGFLOW_SERVER_URL, LANGFLOW_API_KEY, TEST_FLOW_ID]):
    raise ValueError(
        "Missing required environment variables. Please ensure LANGFLOW_SERVER_URL, "
        "LANGFLOW_API_KEY, and LANGFLOW_FLOW_ID are set in your .env file."
    )

@pytest.fixture(scope="session")
def client():
    """Create a LangflowClient instance configured for testing."""
    return LangflowClient({
        "base_url": LANGFLOW_SERVER_URL,
        "api_key": LANGFLOW_API_KEY
    })

@pytest.fixture(scope="session")
def test_flow(client):
    """Get the test flow that echoes back the input."""
    return client.flow(TEST_FLOW_ID)

@pytest.fixture
def test_files_dir():
    """Create and return a temporary directory for test files."""
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup after tests
    shutil.rmtree(test_dir)

@pytest.fixture
def test_file_path(test_files_dir):
    """Create a unique test file for each test."""
    unique_name = f"test_{uuid.uuid4().hex[:8]}.txt"
    file_path = test_files_dir / unique_name
    with open(file_path, "w") as f:
        f.write("This is a test file for Langflow client integration tests.")
    yield str(file_path)
    # File will be cleaned up when test_files_dir is cleaned

@pytest.fixture
def large_test_file_path(test_files_dir):
    """Create a large test file (5MB) for testing large file uploads."""
    file_path = test_files_dir / "large_test.bin"
    size_mb = 5
    with open(file_path, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
    yield str(file_path)

@pytest.fixture
def binary_test_file_path(test_files_dir):
    """Create a binary test file for testing binary file handling."""
    file_path = test_files_dir / "test.bin"
    with open(file_path, "wb") as f:
        f.write(bytes([0x89, 0x50, 0x4E, 0x47]))  # PNG magic number
    yield str(file_path)

@pytest.fixture(autouse=True)
def cleanup_uploaded_files(client):
    """Automatically clean up any files uploaded during tests."""
    yield
    try:
        # List all files and delete them
        files = client.files.list()
        for file in files:
            try:
                client.files.delete(file.id)
            except Exception:
                pass  # Ignore errors during cleanup
    except Exception:
        pass  # Ignore list errors during cleanup 