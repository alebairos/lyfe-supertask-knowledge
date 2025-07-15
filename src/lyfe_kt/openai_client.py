"""
OpenAI client module for Lyfe Supertask Knowledge Generator.

This module provides a simple OpenAI client with error handling, retry logic,
and configuration support for content analysis and generation.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from openai.types.chat import ChatCompletion

from .config_loader import get_config


# Set up logging
logger = logging.getLogger(__name__)


class OpenAIClientError(Exception):
    """Custom exception for OpenAI client errors."""
    pass


class OpenAIClient:
    """
    Simple OpenAI client with error handling and retry logic.
    
    This client provides a wrapper around the OpenAI API with:
    - Configuration-based settings
    - Retry logic for transient failures
    - Error handling and logging
    - Rate limiting awareness
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            config: Optional configuration dictionary. If None, loads from config system.
        """
        self.config = config or get_config('openai')
        self.processing_config = get_config('processing')
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise OpenAIClientError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        
        # Client configuration
        self.model = self.config.get('model', 'gpt-4')
        self.max_tokens = self.config.get('max_tokens', 4000)
        self.temperature = self.config.get('temperature', 0.7)
        self.timeout = self.config.get('timeout', 60)
        
        # Retry configuration
        self.retry_attempts = self.processing_config.get('retry_attempts', 3)
        self.retry_delay = self.processing_config.get('retry_delay', 1.0)
        
        logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def generate_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a completion using the OpenAI API.
        
        Args:
            prompt: The user prompt to send to the model.
            system_message: Optional system message to set context.
            model: Optional model override.
            max_tokens: Optional max tokens override.
            temperature: Optional temperature override.
            
        Returns:
            The generated completion text.
            
        Raises:
            OpenAIClientError: If the API call fails after retries.
        """
        # Use provided parameters or fall back to defaults
        model = model or self.model
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        # Prepare messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Retry logic
        last_error = None
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"OpenAI API call attempt {attempt + 1}/{self.retry_attempts}")
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=self.timeout
                )
                
                # Extract content from response
                if response.choices and response.choices[0].message:
                    content = response.choices[0].message.content
                    if content:
                        logger.debug(f"OpenAI API call successful, response length: {len(content)}")
                        return content.strip()
                
                raise OpenAIClientError("Empty response from OpenAI API")
                
            except Exception as e:
                last_error = e
                logger.warning(f"OpenAI API call failed (attempt {attempt + 1}): {e}")
                
                # Don't retry on certain errors
                if self._is_non_retryable_error(e):
                    break
                
                # Wait before retry (except on last attempt)
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        # All retries failed
        raise OpenAIClientError(f"OpenAI API call failed after {self.retry_attempts} attempts: {last_error}")
    
    def analyze_content(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze content using OpenAI API.
        
        Args:
            content: The content to analyze.
            analysis_type: Type of analysis (general, tone, themes, etc.).
            
        Returns:
            Dictionary containing analysis results.
            
        Raises:
            OpenAIClientError: If the analysis fails.
        """
        # System message for content analysis
        system_message = """You are an expert content analyzer. Analyze the provided content and return structured JSON with the following fields:
- tone: The overall tone (neutral, motivational, inspirational, educational, etc.)
- themes: Array of key themes or topics
- complexity: Content complexity level (beginner, intermediate, advanced)
- language: Detected language (en, pt, etc.)
- key_concepts: Array of main concepts or ideas
- estimated_reading_time: Estimated reading time in minutes"""
        
        # Prepare prompt
        prompt = f"""Analyze the following content and provide structured analysis:

Content:
{content}

Return your analysis as valid JSON only, with no additional text or formatting."""
        
        try:
            response = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            # Try to parse JSON response
            import json
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return basic analysis
                logger.warning("Failed to parse OpenAI analysis response as JSON")
                return {
                    "tone": "neutral",
                    "themes": ["general"],
                    "complexity": "intermediate",
                    "language": "en",
                    "key_concepts": ["content analysis"],
                    "estimated_reading_time": 5
                }
                
        except Exception as e:
            raise OpenAIClientError(f"Content analysis failed: {e}")
    
    def generate_quiz_questions(
        self,
        content: str,
        num_questions: int = 3,
        question_type: str = "multiple_choice"
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions from content.
        
        Args:
            content: The content to generate questions from.
            num_questions: Number of questions to generate.
            question_type: Type of questions (multiple_choice, true_false, etc.).
            
        Returns:
            List of question dictionaries.
            
        Raises:
            OpenAIClientError: If question generation fails.
        """
        # System message for quiz generation
        system_message = """You are an expert quiz generator. Create engaging and educational quiz questions based on the provided content. Return structured JSON with questions that test understanding of key concepts."""
        
        # Prepare prompt based on question type
        if question_type == "multiple_choice":
            prompt = f"""Generate {num_questions} multiple choice questions from this content.
Each question should:
- Test understanding of key concepts
- Have 4 options with 1 correct answer
- Include plausible distractors
- Vary in difficulty

Format as JSON array with objects containing: question, options (array of 4 strings), correct_answer (index 0-3), explanation

Content:
{content}

Return valid JSON only."""
        else:
            prompt = f"""Generate {num_questions} true/false questions from this content.
Focus on:
- Important facts and concepts
- Common misconceptions
- Clear statements that are definitively true or false

Format as JSON array with objects containing: statement, is_true (boolean), explanation

Content:
{content}

Return valid JSON only."""
        
        try:
            response = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.5  # Moderate temperature for creative but accurate questions
            )
            
            # Try to parse JSON response
            import json
            try:
                questions = json.loads(response)
                if isinstance(questions, list):
                    return questions
                else:
                    logger.warning("OpenAI quiz response is not a list")
                    return []
            except json.JSONDecodeError:
                logger.warning("Failed to parse OpenAI quiz response as JSON")
                return []
                
        except Exception as e:
            raise OpenAIClientError(f"Quiz generation failed: {e}")
    
    def enhance_content(self, content: str, enhancement_type: str = "engagement") -> str:
        """
        Enhance content using OpenAI API.
        
        Args:
            content: The content to enhance.
            enhancement_type: Type of enhancement (engagement, clarity, etc.).
            
        Returns:
            Enhanced content string.
            
        Raises:
            OpenAIClientError: If content enhancement fails.
        """
        # System message for content enhancement
        system_message = """You are an expert content editor. Enhance the provided content to make it more engaging, clear, and educational while preserving the original meaning and tone."""
        
        # Prepare prompt
        prompt = f"""Enhance this content to be more engaging by:
- Adding relevant examples or analogies
- Including actionable tips
- Using conversational tone
- Highlighting key insights
- Maintaining the original language and cultural context

Original content:
{content}

Return the enhanced content directly, without additional formatting or explanations."""
        
        try:
            response = self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.6  # Moderate temperature for creative enhancement
            )
            
            return response
            
        except Exception as e:
            raise OpenAIClientError(f"Content enhancement failed: {e}")
    
    def _is_non_retryable_error(self, error: Exception) -> bool:
        """
        Check if an error should not be retried.
        
        Args:
            error: The exception to check.
            
        Returns:
            True if the error should not be retried, False otherwise.
        """
        error_str = str(error).lower()
        
        # Don't retry on authentication errors
        if "authentication" in error_str or "api key" in error_str:
            return True
        
        # Don't retry on permission errors
        if "permission" in error_str or "forbidden" in error_str:
            return True
        
        # Don't retry on quota exceeded (different from rate limiting)
        if "quota" in error_str and "exceeded" in error_str:
            return True
        
        # Don't retry on invalid model errors
        if "model" in error_str and "not found" in error_str:
            return True
        
        return False
    
    def get_client_info(self) -> Dict[str, Any]:
        """
        Get information about the client configuration.
        
        Returns:
            Dictionary with client configuration details.
        """
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay
        }


# Global client instance
_client_instance: Optional[OpenAIClient] = None


def get_openai_client(config: Optional[Dict[str, Any]] = None) -> OpenAIClient:
    """
    Get a global OpenAI client instance.
    
    Args:
        config: Optional configuration dictionary.
        
    Returns:
        OpenAI client instance.
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = OpenAIClient(config)
    
    return _client_instance


def reset_openai_client():
    """Reset the global OpenAI client instance (mainly for testing)."""
    global _client_instance
    _client_instance = None 