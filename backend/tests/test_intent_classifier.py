import pytest
from unittest.mock import patch, MagicMock
from src.services.intent_classifier_dspy import IntentClassifierService

@patch('src.services.intent_classifier_dspy.dspy.LM')
@patch('src.services.intent_classifier_dspy.dspy.Predict')
def test_intent_classifier_crisis(mock_predict, mock_lm):
    """Test that severe self-harm text is classified as crisis."""
    # Mock the DSPy Predictor instance
    mock_classifier_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.intent = "crisis"
    mock_classifier_instance.return_value = mock_response
    mock_predict.return_value = mock_classifier_instance
    
    service = IntentClassifierService()
    result = service.classify_intent("I can't take this anymore, I'm going to end it.")
    
    assert result == "crisis"
    mock_classifier_instance.assert_called_once_with(user_message="I can't take this anymore, I'm going to end it.")

@patch('src.services.intent_classifier_dspy.dspy.LM')
@patch('src.services.intent_classifier_dspy.dspy.Predict')
def test_intent_classifier_out_of_scope_fallback(mock_predict, mock_lm):
    """Test the safety fallback if the LLM generates a hallucinated intent."""
    mock_classifier_instance = MagicMock()
    mock_response = MagicMock()
    # The LLM hallucinates an invalid category
    mock_response.intent = "i_am_confused"
    mock_classifier_instance.return_value = mock_response
    mock_predict.return_value = mock_classifier_instance
    
    service = IntentClassifierService()
    result = service.classify_intent("What is the capital of France?")
    
    # It must fallback to 'out_of_scope' instead of throwing an error
    assert result == "out_of_scope"
