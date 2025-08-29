import json
from pathlib import Path

from langflow_client.flow_response import FlowResponse

FIXTURES = Path(__file__).resolve().parent.parent / "langflow-client-ts" / "src" / "test" / "fixtures"


def test_flow_response_agent():
    data = json.loads((FIXTURES / "agent_response.json").read_text())
    fr = FlowResponse(data)
    assert fr.session_id == data["sessionId"]
    assert fr.outputs == data["outputs"]
    assert isinstance(fr.chat_output_text(), str)


def test_flow_response_model():
    data = json.loads((FIXTURES / "model_response.json").read_text())
    fr = FlowResponse(data)
    assert fr.session_id == data["sessionId"]
    assert fr.outputs == data["outputs"]
    assert isinstance(fr.chat_output_text(), str) 