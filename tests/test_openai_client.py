"""
Tests for OpenAI client module.

This module contains comprehensive tests for the OpenAI client functionality,
including basic operations, error handling, and edge cases.
"""

import os
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the modules to test
from lyfe_kt.openai_client import (
    OpenAIClient,
    OpenAIClientError,
    get_openai_client,
    reset_openai_client
)
from lyfe_kt.config_loader import load_config


class TestOpenAIClientModule:
    """Test that the OpenAI client module structure is correct."""
    
    def test_module_imports(self):
        """Test that all required functions and classes can be imported."""
        from lyfe_kt.openai_client import (
            OpenAIClient,
            OpenAIClientError,
            get_openai_client,
            reset_openai_client
        )
        
        # Check that classes and functions exist
        assert OpenAIClient is not None
        assert OpenAIClientError is not None
        assert get_openai_client is not None
        assert reset_openai_client is not None
    
    def test_exception_inheritance(self):
        """Test that OpenAIClientError inherits from Exception."""
        error = OpenAIClientError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"


class TestOpenAIClientInitialization:
    """Test OpenAI client initialization and configuration."""
    
    def setup_method(self):
        """Set up test environment."""
        # Reset global client instance
        reset_openai_client()
        
        # Mock environment variable
        self.original_api_key = os.environ.get('OPENAI_API_KEY')
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    def teardown_method(self):
        """Clean up test environment."""
        # Restore original API key
        if self.original_api_key:
            os.environ['OPENAI_API_KEY'] = self.original_api_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # Reset global client instance
        reset_openai_client()
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_client_initialization_with_config(self, mock_openai):
        """Test client initialization with configuration."""
        # Load configuration
        config = load_config()
        
        # Create client
        client = OpenAIClient()
        
        # Verify OpenAI client was created
        mock_openai.assert_called_once_with(api_key='test-api-key')
        
        # Verify configuration values
        assert client.model == config['openai']['model']
        assert client.max_tokens == config['openai']['max_tokens']
        assert client.temperature == config['openai']['temperature']
        assert client.timeout == config['openai']['timeout']
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_client_initialization_with_custom_config(self, mock_openai):
        """Test client initialization with custom configuration."""
        custom_config = {
            'model': 'gpt-3.5-turbo',
            'max_tokens': 2000,
            'temperature': 0.5,
            'timeout': 30
        }
        
        # Create client with custom config
        client = OpenAIClient(config=custom_config)
        
        # Verify custom configuration values
        assert client.model == 'gpt-3.5-turbo'
        assert client.max_tokens == 2000
        assert client.temperature == 0.5
        assert client.timeout == 30
    
    def test_client_initialization_without_api_key(self):
        """Test client initialization fails without API key."""
        # Remove API key
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # Should raise error
        with pytest.raises(OpenAIClientError) as exc_info:
            OpenAIClient()
        
        assert "OPENAI_API_KEY environment variable is required" in str(exc_info.value)
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_get_client_info(self, mock_openai):
        """Test getting client configuration information."""
        client = OpenAIClient()
        info = client.get_client_info()
        
        # Verify info contains expected keys
        expected_keys = ['model', 'max_tokens', 'temperature', 'timeout', 'retry_attempts', 'retry_delay']
        for key in expected_keys:
            assert key in info
        
        # Verify values are correct
        assert isinstance(info['model'], str)
        assert isinstance(info['max_tokens'], int)
        assert isinstance(info['temperature'], (int, float))
        assert isinstance(info['timeout'], int)
        assert isinstance(info['retry_attempts'], int)
        assert isinstance(info['retry_delay'], (int, float))


class TestOpenAIClientCompletion:
    """Test OpenAI client completion functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_openai_client()
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    def teardown_method(self):
        """Clean up test environment."""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        reset_openai_client()
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_successful_completion(self, mock_openai):
        """Test successful completion generation."""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response content"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and generate completion
        client = OpenAIClient()
        result = client.generate_completion("Test prompt")
        
        # Verify result
        assert result == "Test response content"
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['messages'] == [{"role": "user", "content": "Test prompt"}]
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_completion_with_system_message(self, mock_openai):
        """Test completion generation with system message."""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and generate completion
        client = OpenAIClient()
        result = client.generate_completion("Test prompt", system_message="System context")
        
        # Verify system message was included
        call_args = mock_client.chat.completions.create.call_args
        expected_messages = [
            {"role": "system", "content": "System context"},
            {"role": "user", "content": "Test prompt"}
        ]
        assert call_args[1]['messages'] == expected_messages
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_completion_with_overrides(self, mock_openai):
        """Test completion generation with parameter overrides."""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and generate completion with overrides
        client = OpenAIClient()
        result = client.generate_completion(
            "Test prompt",
            model="gpt-3.5-turbo",
            max_tokens=1000,
            temperature=0.2
        )
        
        # Verify overrides were used
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == "gpt-3.5-turbo"
        assert call_args[1]['max_tokens'] == 1000
        assert call_args[1]['temperature'] == 0.2
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_completion_empty_response(self, mock_openai):
        """Test handling of empty response from OpenAI."""
        # Mock empty response
        mock_response = Mock()
        mock_response.choices = []
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and attempt completion
        client = OpenAIClient()
        
        with pytest.raises(OpenAIClientError) as exc_info:
            client.generate_completion("Test prompt")
        
        assert "Empty response from OpenAI API" in str(exc_info.value)
    
    @patch('lyfe_kt.openai_client.OpenAI')
    @patch('time.sleep')
    def test_completion_retry_logic(self, mock_sleep, mock_openai):
        """Test retry logic for transient failures."""
        # Mock client that fails twice then succeeds
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("Temporary error"),
            Exception("Another temporary error"),
            self._create_successful_response("Success after retries")
        ]
        mock_openai.return_value = mock_client
        
        # Create client and generate completion
        client = OpenAIClient()
        result = client.generate_completion("Test prompt")
        
        # Verify success after retries
        assert result == "Success after retries"
        
        # Verify retry calls
        assert mock_client.chat.completions.create.call_count == 3
        assert mock_sleep.call_count == 2  # Two sleeps between three attempts
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_completion_non_retryable_error(self, mock_openai):
        """Test handling of non-retryable errors."""
        # Mock client with authentication error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Authentication error")
        mock_openai.return_value = mock_client
        
        # Create client and attempt completion
        client = OpenAIClient()
        
        with pytest.raises(OpenAIClientError) as exc_info:
            client.generate_completion("Test prompt")
        
        # Verify only one attempt was made
        assert mock_client.chat.completions.create.call_count == 1
        assert "Authentication error" in str(exc_info.value)
    
    def _create_successful_response(self, content: str):
        """Helper to create a successful OpenAI response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = content
        return mock_response


class TestOpenAIClientContentAnalysis:
    """Test OpenAI client content analysis functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_openai_client()
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    def teardown_method(self):
        """Clean up test environment."""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        reset_openai_client()
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_successful_content_analysis(self, mock_openai):
        """Test successful content analysis."""
        # Mock JSON response
        analysis_result = {
            "tone": "motivational",
            "themes": ["productivity", "morning routine"],
            "complexity": "intermediate",
            "language": "en",
            "key_concepts": ["habits", "consistency"],
            "estimated_reading_time": 3
        }
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps(analysis_result)
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and analyze content
        client = OpenAIClient()
        result = client.analyze_content("Test content for analysis")
        
        # Verify result
        assert result == analysis_result
        assert result["tone"] == "motivational"
        assert "productivity" in result["themes"]
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_content_analysis_invalid_json(self, mock_openai):
        """Test content analysis with invalid JSON response."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and analyze content
        client = OpenAIClient()
        result = client.analyze_content("Test content")
        
        # Verify fallback result
        assert result["tone"] == "neutral"
        assert result["themes"] == ["general"]
        assert result["complexity"] == "intermediate"
        assert result["language"] == "en"
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_content_analysis_api_failure(self, mock_openai):
        """Test content analysis with API failure."""
        # Mock API failure
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API failure")
        mock_openai.return_value = mock_client
        
        # Create client and attempt analysis
        client = OpenAIClient()
        
        with pytest.raises(OpenAIClientError) as exc_info:
            client.analyze_content("Test content")
        
        assert "Content analysis failed" in str(exc_info.value)


class TestOpenAIClientQuizGeneration:
    """Test OpenAI client quiz generation functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_openai_client()
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    def teardown_method(self):
        """Clean up test environment."""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        reset_openai_client()
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_successful_multiple_choice_generation(self, mock_openai):
        """Test successful multiple choice quiz generation."""
        # Mock quiz response
        quiz_result = [
            {
                "question": "What is the main benefit of morning routines?",
                "options": ["Better sleep", "Increased productivity", "More energy", "Better mood"],
                "correct_answer": 1,
                "explanation": "Morning routines help structure the day for better productivity."
            }
        ]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps(quiz_result)
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and generate quiz
        client = OpenAIClient()
        result = client.generate_quiz_questions("Test content", num_questions=1)
        
        # Verify result
        assert len(result) == 1
        assert result[0]["question"] == "What is the main benefit of morning routines?"
        assert len(result[0]["options"]) == 4
        assert result[0]["correct_answer"] == 1
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_successful_true_false_generation(self, mock_openai):
        """Test successful true/false quiz generation."""
        # Mock quiz response
        quiz_result = [
            {
                "statement": "Morning routines always improve productivity",
                "is_true": False,
                "explanation": "While helpful, morning routines don't guarantee productivity improvements for everyone."
            }
        ]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps(quiz_result)
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and generate quiz
        client = OpenAIClient()
        result = client.generate_quiz_questions("Test content", num_questions=1, question_type="true_false")
        
        # Verify result
        assert len(result) == 1
        assert result[0]["statement"] == "Morning routines always improve productivity"
        assert result[0]["is_true"] is False
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_quiz_generation_invalid_json(self, mock_openai):
        """Test quiz generation with invalid JSON response."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Invalid JSON"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and generate quiz
        client = OpenAIClient()
        result = client.generate_quiz_questions("Test content")
        
        # Verify empty result
        assert result == []
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_quiz_generation_api_failure(self, mock_openai):
        """Test quiz generation with API failure."""
        # Mock API failure
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API failure")
        mock_openai.return_value = mock_client
        
        # Create client and attempt quiz generation
        client = OpenAIClient()
        
        with pytest.raises(OpenAIClientError) as exc_info:
            client.generate_quiz_questions("Test content")
        
        assert "Quiz generation failed" in str(exc_info.value)


class TestOpenAIClientContentEnhancement:
    """Test OpenAI client content enhancement functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_openai_client()
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    def teardown_method(self):
        """Clean up test environment."""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        reset_openai_client()
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_successful_content_enhancement(self, mock_openai):
        """Test successful content enhancement."""
        # Mock enhanced content response
        enhanced_content = "Enhanced version of the original content with better examples and clearer explanations."
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = enhanced_content
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and enhance content
        client = OpenAIClient()
        result = client.enhance_content("Original content")
        
        # Verify result
        assert result == enhanced_content
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_content_enhancement_api_failure(self, mock_openai):
        """Test content enhancement with API failure."""
        # Mock API failure
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API failure")
        mock_openai.return_value = mock_client
        
        # Create client and attempt enhancement
        client = OpenAIClient()
        
        with pytest.raises(OpenAIClientError) as exc_info:
            client.enhance_content("Original content")
        
        assert "Content enhancement failed" in str(exc_info.value)


class TestOpenAIClientErrorHandling:
    """Test OpenAI client error handling functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_openai_client()
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    def teardown_method(self):
        """Clean up test environment."""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        reset_openai_client()
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_non_retryable_error_detection(self, mock_openai):
        """Test detection of non-retryable errors."""
        client = OpenAIClient()
        
        # Test various non-retryable errors
        non_retryable_errors = [
            "Authentication error",
            "Invalid API key",
            "Permission denied",
            "Quota exceeded permanently",
            "Model not found error"
        ]
        
        for error_msg in non_retryable_errors:
            error = Exception(error_msg)
            assert client._is_non_retryable_error(error) is True
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_retryable_error_detection(self, mock_openai):
        """Test detection of retryable errors."""
        client = OpenAIClient()
        
        # Test various retryable errors
        retryable_errors = [
            "Rate limit exceeded",
            "Temporary network error",
            "Service unavailable",
            "Timeout error"
        ]
        
        for error_msg in retryable_errors:
            error = Exception(error_msg)
            assert client._is_non_retryable_error(error) is False


class TestOpenAIClientGlobalInstance:
    """Test OpenAI client global instance management."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_openai_client()
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    def teardown_method(self):
        """Clean up test environment."""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        reset_openai_client()
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_global_client_instance(self, mock_openai):
        """Test global client instance creation and reuse."""
        # Get client instance twice
        client1 = get_openai_client()
        client2 = get_openai_client()
        
        # Should be the same instance
        assert client1 is client2
        
        # Should only create OpenAI client once
        assert mock_openai.call_count == 1
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_reset_global_client(self, mock_openai):
        """Test resetting global client instance."""
        # Get client instance
        client1 = get_openai_client()
        
        # Reset and get new instance
        reset_openai_client()
        client2 = get_openai_client()
        
        # Should be different instances
        assert client1 is not client2
        
        # Should create OpenAI client twice
        assert mock_openai.call_count == 2
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_global_client_with_custom_config(self, mock_openai):
        """Test global client with custom configuration."""
        custom_config = {
            'model': 'gpt-3.5-turbo',
            'max_tokens': 1000,
            'temperature': 0.3,
            'timeout': 30
        }
        
        # Get client with custom config
        client = get_openai_client(config=custom_config)
        
        # Verify custom configuration
        assert client.model == 'gpt-3.5-turbo'
        assert client.max_tokens == 1000
        assert client.temperature == 0.3
        assert client.timeout == 30


class TestOpenAIClientIntegration:
    """Test OpenAI client integration scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_openai_client()
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
    
    def teardown_method(self):
        """Clean up test environment."""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        reset_openai_client()
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_unicode_content_handling(self, mock_openai):
        """Test handling of Unicode content."""
        # Mock response with Unicode content
        unicode_content = "Conteúdo em português com acentos: ção, ã, ê"
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = unicode_content
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and process Unicode content
        client = OpenAIClient()
        result = client.generate_completion("Prompt with Unicode: café")
        
        # Verify Unicode handling
        assert result == unicode_content
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_large_content_handling(self, mock_openai):
        """Test handling of large content."""
        # Create large content
        large_content = "Large content. " * 1000  # ~14KB of text
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Processed large content successfully"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create client and process large content
        client = OpenAIClient()
        result = client.generate_completion(large_content)
        
        # Verify large content handling
        assert result == "Processed large content successfully"
        
        # Verify the large content was passed to API
        call_args = mock_client.chat.completions.create.call_args
        assert large_content in call_args[1]['messages'][0]['content']
    
    @patch('lyfe_kt.openai_client.OpenAI')
    def test_concurrent_requests_simulation(self, mock_openai):
        """Test simulation of concurrent requests."""
        # Mock responses for multiple requests
        mock_responses = []
        for i in range(3):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = f"Response {i+1}"
            mock_responses.append(mock_response)
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = mock_responses
        mock_openai.return_value = mock_client
        
        # Create client and make multiple requests
        client = OpenAIClient()
        results = []
        for i in range(3):
            result = client.generate_completion(f"Prompt {i+1}")
            results.append(result)
        
        # Verify all requests succeeded
        assert results == ["Response 1", "Response 2", "Response 3"]
        assert mock_client.chat.completions.create.call_count == 3 