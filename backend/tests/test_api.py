import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.main import app

client = TestClient(app)

def test_health_check():
    """Ensure the API is up and running."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_empty_query():
    """Ensure the API rejects empty queries."""
    response = client.post("/chat", json={"query": "   "})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"].lower()

@patch("src.api.main.intent_service")
@patch("src.api.main.translator_service")
def test_chat_out_of_scope(mock_translator, mock_intent):
    """
    Test the out_of_scope intent routing.
    We mock the ML/LLM services so this test runs instantly without API keys.
    """
    # 1. Setup the mocks
    mock_translator.process_prompt.return_value = {
        "language": "en",
        "english_text": "Write me a python script"
    }
    mock_intent.classify_intent.return_value = "out_of_scope"
    
    # 2. Call the endpoint
    response = client.post("/chat", json={"query": "Write me a python script"})
    
    # 3. Assert correct behavior
    assert response.status_code == 200
    data = response.json()
    assert data["detected_intent"] == "out_of_scope"
    assert data["detected_language"] == "en"
    
    # The response should be the static fallback, not an LLM generation
    assert "mental health" in data["response"].lower()

@patch("src.api.main.intent_service")
@patch("src.api.main.translator_service")
def test_chat_crisis(mock_translator, mock_intent):
    """Test the priority-0 crisis guardrail."""
    mock_translator.process_prompt.return_value = {
        "language": "en",
        "english_text": "I want to hurt myself."
    }
    mock_intent.classify_intent.return_value = "crisis"
    
    response = client.post("/chat", json={"query": "I want to hurt myself."})
    
    assert response.status_code == 200
    data = response.json()
    assert data["detected_intent"] == "crisis"
    assert "emergency" in data["response"].lower() or "hotline" in data["response"].lower()
