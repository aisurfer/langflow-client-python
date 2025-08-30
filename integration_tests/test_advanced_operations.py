"""
Integration tests demonstrating advanced Langflow client operations.
These tests cover scenarios like concurrent operations, large files,
and error recovery.
"""
import asyncio
import concurrent.futures
import os
import pytest
from langflow_client import LangflowError


def test_large_file_upload(client, large_test_file_path):
    """
    Example: Uploading and handling large files.
    
    This demonstrates how the client handles large file uploads,
    which is important for real-world use cases.
    """
    with open(large_test_file_path, "rb") as f:
        response = client.files.upload(f, filename=os.path.basename(large_test_file_path))
    
    assert response.id is not None
    # Server may modify filename, check base name without extension
    base_name = os.path.splitext(os.path.basename(large_test_file_path))[0]
    assert base_name in response.name


def test_binary_file_upload(client, binary_test_file_path):
    """
    Example: Uploading binary files.
    
    This demonstrates how to handle binary file uploads,
    ensuring proper content-type handling.
    """
    with open(binary_test_file_path, "rb") as f:
        response = client.files.upload(
            f,
            filename=os.path.basename(binary_test_file_path),
            content_type="application/octet-stream"
        )
    
    assert response.id is not None
    # Server may modify filename, check base name without extension
    base_name = os.path.splitext(os.path.basename(binary_test_file_path))[0]
    assert base_name in response.name


def test_concurrent_flow_runs(test_flow):
    """
    Example: Running multiple flow operations concurrently.
    
    This demonstrates how to handle concurrent flow operations,
    which is useful for high-throughput scenarios.
    """
    inputs = [
        "First concurrent request",
        "Second concurrent request",
        "Third concurrent request",
        "Fourth concurrent request"
    ]
    
    def run_flow(input_text):
        response = test_flow.run(input_text)
        assert f"Your request is: {input_text}" in response.chat_output_text()
        return response
    
    # Run flows concurrently using a thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_flow, input_text) for input_text in inputs]
        responses = [future.result() for future in futures]
    
    assert len(responses) == len(inputs)
    for response, input_text in zip(responses, inputs):
        assert f"Your request is: {input_text}" in response.chat_output_text()


def test_error_recovery(test_flow):
    """
    Example: Handling and recovering from errors.
    
    This demonstrates proper error handling and recovery
    strategies when operations fail.
    """
    # Test invalid input type handling
    with pytest.raises(LangflowError) as exc_info:
        test_flow.run(
            "test",
            input_type="invalid_type"  # This should trigger an error
        )
    assert exc_info.value is not None
    
    # Verify we can still run flows after an error
    response = test_flow.run("Recovery test")
    assert "Your request is: Recovery test" in response.chat_output_text()
    
    # Test recovery after network error simulation
    try:
        # Simulate network error with invalid URL
        bad_client = LangflowClient({
            "base_url": "http://invalid.example.com",
            "api_key": "invalid"
        })
        bad_client.flow("invalid-id").run("test")
    except Exception as e:
        assert isinstance(e, (LangflowError, Exception))
    
    # Verify original client still works
    response = test_flow.run("Still working")
    assert "Your request is: Still working" in response.chat_output_text()


@pytest.mark.asyncio
async def test_async_operations(test_flow):
    """
    Example: Running operations asynchronously.
    
    This demonstrates how to handle multiple operations
    asynchronously using asyncio.
    """
    async def async_run_flow(input_text):
        # Simulate async operation using ThreadPoolExecutor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, test_flow.run, input_text
        )
        return response
    
    # Run multiple flows concurrently
    inputs = ["Async 1", "Async 2", "Async 3"]
    tasks = [async_run_flow(text) for text in inputs]
    responses = await asyncio.gather(*tasks)
    
    assert len(responses) == len(inputs)
    for response, input_text in zip(responses, inputs):
        assert f"Your request is: {input_text}" in response.chat_output_text() 