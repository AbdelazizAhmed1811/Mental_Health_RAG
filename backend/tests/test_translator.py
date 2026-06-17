import pytest
from unittest.mock import patch, MagicMock
from src.services.translator import TranslatorService

@patch('src.services.translator.joblib.load')
def test_translator_detect_language(mock_load):
    """Test that the internal language model is correctly used to detect language."""
    # Setup mock model
    mock_pipeline = MagicMock()
    mock_pipeline.predict.return_value = ['es']
    mock_load.return_value = mock_pipeline
    
    translator = TranslatorService()
    
    result = translator.detect_language("Me siento triste")
    
    assert result == "es"
    mock_pipeline.predict.assert_called_once_with(["Me siento triste"])

@patch('src.services.translator.GoogleTranslator')
@patch('src.services.translator.joblib.load')
def test_translator_process_prompt_non_english(mock_load, mock_google_translator):
    """Test full pipeline: detecting a non-English language and translating it to English."""
    # Mock language detection to return 'ar'
    mock_pipeline = MagicMock()
    mock_pipeline.predict.return_value = ['ar']
    mock_load.return_value = mock_pipeline
    
    # Mock translation to return English equivalent
    mock_translator_instance = mock_google_translator.return_value
    mock_translator_instance.translate.return_value = "Hello, I am sad."
    
    translator = TranslatorService()
    result = translator.process_prompt("مرحبا، أنا حزين.")
    
    assert result["language"] == "ar"
    assert result["original_text"] == "مرحبا، أنا حزين."
    assert result["english_text"] == "Hello, I am sad."

@patch('src.services.translator.joblib.load')
def test_translator_process_prompt_english(mock_load):
    """Test that English text bypasses the translation step."""
    # Mock language detection to return 'en'
    mock_pipeline = MagicMock()
    mock_pipeline.predict.return_value = ['en']
    mock_load.return_value = mock_pipeline
    
    translator = TranslatorService()
    result = translator.process_prompt("I am fine.")
    
    assert result["language"] == "en"
    assert result["english_text"] == "I am fine."
