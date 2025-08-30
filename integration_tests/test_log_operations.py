"""
Integration tests demonstrating Langflow client log operations.
These tests serve as examples of how to use the logging-related features.
"""
from datetime import datetime, timedelta
import time
import pytest
from langflow_client import Log


@pytest.mark.skip(reason="Log API not implemented in server")
def test_fetch_logs(client):
    """
    Example: Fetching logs from Langflow.
    
    This demonstrates how to retrieve logs from the system,
    which is useful for monitoring and debugging.
    """
    # First generate some logs by running a flow
    flow = client.flow("ea0736a1-1f55-4a06-91fd-7b9ef43e08aa")
    flow.run("Generate some logs")
    
    # Wait briefly for logs to be processed
    time.sleep(1)
    
    # Fetch recent logs
    logs = list(client.logs.fetch())
    
    assert len(logs) > 0
    assert all(isinstance(log, Log) for log in logs)
    
    # Each log should have timestamp and message
    for log in logs:
        assert isinstance(log.timestamp, int)  # Timestamp is Unix timestamp
        assert isinstance(log.message, str)


@pytest.mark.skip(reason="Log API not implemented in server")
def test_logs_with_timestamp(client):
    """
    Example: Fetching logs around a specific timestamp.
    
    This shows how to fetch logs around a specific point in time,
    which is useful for investigating issues.
    """
    # Generate a log entry
    flow = client.flow("ea0736a1-1f55-4a06-91fd-7b9ef43e08aa")
    flow.run("Generate log for timestamp test")
    
    # Wait briefly for logs to be processed
    time.sleep(1)
    
    # Get current timestamp
    current_time = int(time.time())
    
    # Fetch logs around current timestamp
    logs = list(client.logs.fetch(
        timestamp=current_time,
        lines_before=10,
        lines_after=10
    ))
    
    assert len(logs) > 0
    for log in logs:
        assert isinstance(log.timestamp, int)
        assert isinstance(log.message, str)


@pytest.mark.skip(reason="Log API not implemented in server")
def test_log_streaming(client):
    """
    Example: Streaming logs in real-time.
    
    This demonstrates how to stream logs as they are generated,
    which is useful for real-time monitoring.
    """
    # Start log stream
    stream = client.logs.stream()
    
    # Generate some logs by running a flow
    flow = client.flow("ea0736a1-1f55-4a06-91fd-7b9ef43e08aa")
    flow.run("Generate logs while streaming")
    
    # Read a few log entries
    log_count = 0
    for log in stream:
        assert isinstance(log, Log)
        log_count += 1
        if log_count >= 5:  # Stop after 5 logs
            break
    
    assert log_count > 0 