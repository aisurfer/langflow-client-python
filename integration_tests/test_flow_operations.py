"""
Integration tests demonstrating Langflow client flow operations.
These tests serve as examples of how to use the flow-related features.
"""
import pytest
from langflow_client import InputTypes, OutputTypes, LangflowError
from langflow_client.flow_response import FlowResponse


def test_basic_flow_run(test_flow):
    """
    Example: Basic flow execution with default input/output types.
    
    This demonstrates the simplest way to run a flow and get a response.
    The test flow is configured to echo back the input.
    """
    test_input = "Hello, Langflow!"
    response = test_flow.run(test_input)
    
    assert isinstance(response, FlowResponse)
    assert "Your request is: Hello, Langflow!" in response.chat_output_text()


def test_flow_with_different_types(test_flow):
    """
    Example: Running flow with different input/output types.
    
    This shows how to specify different input and output types
    when running a flow.
    """
    test_input = "Process this text"
    response = test_flow.run(
        test_input,
        input_type=InputTypes.TEXT,
        output_type=OutputTypes.TEXT
    )
    
    assert isinstance(response, FlowResponse)
    assert response.outputs is not None
    # For text output type, we get the raw output
    assert isinstance(response.outputs, list), "Outputs should be a list"
    assert len(response.outputs) > 0, "Outputs list should not be empty"
    output_text = str(response.outputs[0])  # Get first output
    assert test_input in output_text, "Response should contain the input text"


def test_flow_with_tweaks(test_flow):
    """
    Example: Using tweaks to modify flow behavior.
    
    This demonstrates how to use tweaks to customize the flow's
    behavior at runtime without modifying the flow itself.
    """
    # Create a tweaked version of the flow
    tweaked_flow = test_flow.tweak(
        "system_message", 
        "You are a helpful assistant that prefixes responses with 'Bot:'"
    )
    
    test_input = "Hello!"
    response = tweaked_flow.run(test_input)
    assert isinstance(response, FlowResponse)
    # Verify the expected response format
    assert test_input in response.chat_output_text()


def test_flow_streaming(test_flow):
    """
    Example: Using streaming response from a flow.
    
    This shows how to handle streaming responses from a flow,
    which is useful for real-time updates and long-running operations.
    """
    test_input = "Generate a long response"
    stream = test_flow.stream(test_input)
    
    # Collect all chunks
    chunks = list(stream)
    assert len(chunks) > 0
    
    # Each chunk should be a dict with expected structure
    found_message = False
    full_content = []
    
    for chunk in chunks:
        assert isinstance(chunk, dict)
        assert "event" in chunk
        assert chunk["event"] in ["add_message", "end", "error"]
        if chunk["event"] == "add_message":
            assert "data" in chunk
            data = chunk["data"]
            # Extract text from message data
            if isinstance(data, dict) and "text" in data:
                full_content.append(data["text"])
    
    # Join all content
    complete_content = " ".join(full_content)
    
    # Verify we got the expected response
    assert len(complete_content.strip()) > 0, "Response should not be empty"
    # The echo flow should include our input somewhere in the response
    assert any(test_input in content for content in full_content), \
        f"Expected '{test_input}' in one of the response chunks. Got chunks: {full_content}"
    
    # Verify we got both user message and response
    user_messages = [msg for msg in full_content if msg == test_input]
    ai_messages = [msg for msg in full_content if "Your request is:" in msg]
    assert len(user_messages) > 0, "Should include user message"
    assert len(ai_messages) > 0, "Should include AI response"


def test_flow_with_session(test_flow):
    """
    Example: Using session ID for stateful conversations.
    
    This demonstrates how to maintain conversation state
    across multiple flow runs using a session ID.
    """
    session_id = "test-session-123"
    
    # First message in conversation
    first_message = "First message"
    response1 = test_flow.run(
        first_message,
        session_id=session_id
    )
    assert isinstance(response1, FlowResponse)
    assert first_message in response1.chat_output_text()
    
    # Second message in same conversation
    second_message = "Second message"
    response2 = test_flow.run(
        second_message,
        session_id=session_id
    )
    assert isinstance(response2, FlowResponse)
    assert second_message in response2.chat_output_text()


def test_error_handling(test_flow):
    """
    Example: Handling errors in flow execution.
    
    This shows how to properly handle various error cases
    that might occur during flow execution.
    """
    with pytest.raises(LangflowError) as exc_info:
        # Attempt to run flow with invalid input type
        test_flow.run(
            "test",
            input_type="invalid_type"
        )
    
    assert exc_info.value is not None
    # Error message should be informative
    error_message = str(exc_info.value)
    assert error_message != ""
    assert "422" in error_message, "Error should be a 422 Unprocessable Entity"
    
    # Test recovery after error
    recovery_input = "Recovery test"
    response = test_flow.run(recovery_input)
    assert recovery_input in response.chat_output_text() 