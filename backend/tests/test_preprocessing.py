import pytest
from src.utils.preprocessing import PreprocessingService

def test_preprocess_query_empty():
    assert PreprocessingService.preprocess_query("") == ""
    assert PreprocessingService.preprocess_query(None) == ""

def test_preprocess_query_strip_whitespace():
    assert PreprocessingService.preprocess_query("   Hello World   ") == "Hello World"
    # Multiple internal spaces/newlines should be normalized to one
    assert PreprocessingService.preprocess_query("Hello   \n\t  World") == "Hello World"

def test_preprocess_query_strip_quotes():
    assert PreprocessingService.preprocess_query('"Hello"') == "Hello"
    assert PreprocessingService.preprocess_query("'Help me'") == "Help me"
    # Nested quotes should be stripped recursively
    assert PreprocessingService.preprocess_query('""Nested""') == "Nested"

def test_preprocess_query_remove_unwanted_signs():
    # Should keep basic punctuation needed for emotion context
    assert PreprocessingService.preprocess_query("I'm sad...") == "I'm sad..."
    assert PreprocessingService.preprocess_query("Why?! (yes)") == "Why?! (yes)"
    
    # Should remove weird special symbols
    assert PreprocessingService.preprocess_query("Help @### me $$%") == "Help me "
    
    # Should preserve non-English unicode characters (like Arabic)
    assert PreprocessingService.preprocess_query("مرحبا العالم @#$") == "مرحبا العالم "
