import pytest
from unittest.mock import patch, MagicMock
from src.services.rag_service_dspy import RAGService

@patch('src.services.rag_service_dspy.QdrantClient')
@patch('src.services.rag_service_dspy.SentenceTransformer')
@patch('src.services.rag_service_dspy.dspy.LM')
@patch('src.services.rag_service_dspy.dspy.Predict')
def test_rag_generate_response_success(mock_predict, mock_lm, mock_transformer, mock_qdrant):
    """Test that the RAG service successfully retrieves context and generates a response."""
    # Mock Qdrant Client to return empty context for simplicity
    mock_qdrant_instance = mock_qdrant.return_value
    mock_qdrant_instance.query_points.return_value.points = []
    
    # Mock Embedding Model to simulate numpy array behavior for .tolist()
    mock_encode_result = MagicMock()
    mock_encode_result.tolist.return_value = [0.1, 0.2, 0.3]
    mock_transformer_instance = mock_transformer.return_value
    mock_transformer_instance.encode.return_value = mock_encode_result
    
    # Mock DSPy Generator
    mock_generator_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.response = "I hear you, and I am here to help you through this sadness."
    mock_generator_instance.return_value = mock_response
    mock_predict.return_value = mock_generator_instance
    
    service = RAGService()
    result = service.generate_response(query="I feel sad today.", emotion="sadness", language_code="en")
    
    assert result == "I hear you, and I am here to help you through this sadness."
    
    # Verify DSPy was called with the correct parameters
    mock_generator_instance.assert_called_once()
    call_kwargs = mock_generator_instance.call_args.kwargs
    assert call_kwargs["user_emotion"] == "SADNESS"
    assert call_kwargs["user_message"] == "I feel sad today."
    assert call_kwargs["target_language"] == "en"

@patch('src.services.rag_service_dspy.QdrantClient')
@patch('src.services.rag_service_dspy.SentenceTransformer')
@patch('src.services.rag_service_dspy.dspy.LM')
@patch('src.services.rag_service_dspy.dspy.Predict')
def test_rag_generate_response_error_handling(mock_predict, mock_lm, mock_transformer, mock_qdrant):
    """Test that exceptions from DSPy are correctly caught and re-raised as RuntimeErrors."""
    # Mock Qdrant Client
    mock_qdrant_instance = mock_qdrant.return_value
    mock_qdrant_instance.query_points.return_value.points = []
    
    # Mock DSPy Generator to throw an error (e.g. API key limit reached)
    mock_generator_instance = MagicMock()
    mock_generator_instance.side_effect = Exception("llm API rate limit exceeded")
    mock_predict.return_value = mock_generator_instance
    
    service = RAGService()
    
    with pytest.raises(RuntimeError) as exc_info:
        service.generate_response(query="Help", emotion="anxiety", language_code="en")
        
    assert "Failed to generate response: llm API rate limit exceeded" in str(exc_info.value)
