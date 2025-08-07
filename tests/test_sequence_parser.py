"""
Tests for SequenceParser - Configurable Narrative Sequences

These tests follow the defensive testing approach:
- Very focused: Each test targets a specific scenario
- Simple: Tests are straightforward and easy to understand  
- No mocks needed: We test the actual SequenceParser logic
- Easy to understand and maintain: Clear assertions and comments
- One test at a time: Each test focuses on a single functionality aspect
"""

import pytest
from src.lyfe_kt.stage3_generation import SequenceParser


class TestSequenceParserBasics:
    """Test basic functionality of SequenceParser."""
    
    def test_default_sequence_is_valid(self):
        """Test that the default sequence is valid."""
        default = SequenceParser.get_default_sequence()
        
        # Should return the expected default pattern
        assert default == ['content', 'quiz', 'content', 'quote', 'content', 'quiz']
        
        # Default should pass validation
        assert SequenceParser.validate_sequence(default) is True
    
    def test_parse_valid_sequence_simple(self):
        """Test parsing a simple valid sequence."""
        sequence_str = "content → quiz → quote"
        result = SequenceParser.parse_sequence(sequence_str)
        
        assert result == ['content', 'quiz', 'quote']
    
    def test_parse_valid_sequence_complex(self):
        """Test parsing a more complex valid sequence."""
        sequence_str = "quote → content → quiz → content → quiz → quote"
        result = SequenceParser.parse_sequence(sequence_str)
        
        assert result == ['quote', 'content', 'quiz', 'content', 'quiz', 'quote']
    
    def test_parse_empty_sequence_returns_default(self):
        """Test that empty sequence returns default."""
        # Empty string
        result = SequenceParser.parse_sequence("")
        assert result == SequenceParser.get_default_sequence()
        
        # None
        result = SequenceParser.parse_sequence(None)
        assert result == SequenceParser.get_default_sequence()
        
        # Whitespace only
        result = SequenceParser.parse_sequence("   ")
        assert result == SequenceParser.get_default_sequence()
    
    def test_parse_sequence_with_extra_whitespace(self):
        """Test parsing sequence with extra whitespace."""
        sequence_str = "  content  →  quiz  →  quote  "
        result = SequenceParser.parse_sequence(sequence_str)
        
        assert result == ['content', 'quiz', 'quote']


class TestSequenceParserValidation:
    """Test validation rules for sequences."""
    
    def test_validate_minimum_length(self):
        """Test that sequences must have at least 3 items."""
        # Valid minimum length
        valid_sequence = ['content', 'quiz', 'quote']
        assert SequenceParser.validate_sequence(valid_sequence) is True
        
        # Too short sequences should raise ValueError
        with pytest.raises(ValueError, match="must have at least 3 items"):
            SequenceParser.validate_sequence(['content', 'quiz'])
        
        with pytest.raises(ValueError, match="must have at least 3 items"):
            SequenceParser.validate_sequence(['content'])
    
    def test_validate_maximum_length(self):
        """Test that sequences cannot exceed 8 items."""
        # Valid maximum length
        valid_sequence = ['content', 'quiz', 'content', 'quote', 'content', 'quiz', 'content', 'quote']
        assert SequenceParser.validate_sequence(valid_sequence) is True
        
        # Too long sequence should raise ValueError
        too_long = ['content'] * 9
        with pytest.raises(ValueError, match="must have at most 8 items"):
            SequenceParser.validate_sequence(too_long)
    
    def test_validate_requires_all_types(self):
        """Test that sequences must include at least one of each type."""
        # Valid - has all types
        valid_sequence = ['content', 'quiz', 'quote']
        assert SequenceParser.validate_sequence(valid_sequence) is True
        
        # Missing quiz
        with pytest.raises(ValueError, match="Missing: quiz"):
            SequenceParser.validate_sequence(['content', 'content', 'quote'])
        
        # Missing quote  
        with pytest.raises(ValueError, match="Missing: quote"):
            SequenceParser.validate_sequence(['content', 'quiz', 'content'])
        
        # Missing content
        with pytest.raises(ValueError, match="Missing: content"):
            SequenceParser.validate_sequence(['quiz', 'quote', 'quiz'])
    
    def test_validate_invalid_types(self):
        """Test that invalid item types are rejected."""
        with pytest.raises(ValueError, match="Invalid item types: unknown"):
            SequenceParser.validate_sequence(['content', 'quiz', 'unknown'])
        
        with pytest.raises(ValueError, match="Invalid item types"):
            SequenceParser.validate_sequence(['content', 'quiz', 'video', 'audio'])
    
    def test_validate_empty_sequence(self):
        """Test that empty sequences are rejected."""
        with pytest.raises(ValueError, match="Sequence cannot be empty"):
            SequenceParser.validate_sequence([])


class TestSequenceParserErrorHandling:
    """Test error handling and edge cases."""
    
    def test_parse_invalid_separator(self):
        """Test parsing with wrong separator."""
        # Using wrong separator should still work by treating as single item
        sequence_str = "content - quiz - quote"  # Wrong separator
        
        # This should raise an error because "content - quiz - quote" is not a valid type
        with pytest.raises(ValueError, match="Invalid item type"):
            SequenceParser.parse_sequence(sequence_str)
    
    def test_parse_invalid_item_types(self):
        """Test parsing with invalid item types."""
        with pytest.raises(ValueError, match="Invalid item type 'video'"):
            SequenceParser.parse_sequence("content → quiz → video")
        
        with pytest.raises(ValueError, match="Invalid item type 'unknown'"):
            SequenceParser.parse_sequence("content → unknown → quote")
    
    def test_parse_mixed_case_types(self):
        """Test that item types are case sensitive."""
        with pytest.raises(ValueError, match="Invalid item type 'Content'"):
            SequenceParser.parse_sequence("Content → quiz → quote")
        
        with pytest.raises(ValueError, match="Invalid item type 'QUIZ'"):
            SequenceParser.parse_sequence("content → QUIZ → quote")
    
    def test_parse_empty_items_after_split(self):
        """Test handling of empty items after splitting."""
        # Multiple arrows in sequence
        sequence_str = "content → → quiz → quote"
        result = SequenceParser.parse_sequence(sequence_str)
        
        # Should ignore empty items and work correctly
        assert result == ['content', 'quiz', 'quote']
    
    def test_constants_are_correct(self):
        """Test that class constants have expected values."""
        assert SequenceParser.DEFAULT_SEQUENCE == ['content', 'quiz', 'content', 'quote', 'content', 'quiz']
        assert SequenceParser.VALID_TYPES == {'content', 'quiz', 'quote'}
        assert SequenceParser.MIN_ITEMS == 3
        assert SequenceParser.MAX_ITEMS == 8


class TestSequenceParserRealWorldPatterns:
    """Test realistic sequence patterns that users might want."""
    
    def test_motivation_first_pattern(self):
        """Test quote → content → quiz pattern (motivation first)."""
        sequence_str = "quote → content → quiz → content → quiz → quote"
        result = SequenceParser.parse_sequence(sequence_str)
        
        assert result == ['quote', 'content', 'quiz', 'content', 'quiz', 'quote']
        assert SequenceParser.validate_sequence(result) is True
    
    def test_assessment_first_pattern(self):
        """Test quiz → content → quote pattern (assessment first)."""
        sequence_str = "quiz → content → quote → content → quiz → content"
        result = SequenceParser.parse_sequence(sequence_str)
        
        assert result == ['quiz', 'content', 'quote', 'content', 'quiz', 'content']
        assert SequenceParser.validate_sequence(result) is True
    
    def test_deep_learning_pattern(self):
        """Test content → content → quiz pattern (deep learning)."""
        sequence_str = "content → content → quiz → quote → content → quiz"
        result = SequenceParser.parse_sequence(sequence_str)
        
        assert result == ['content', 'content', 'quiz', 'quote', 'content', 'quiz']
        assert SequenceParser.validate_sequence(result) is True
    
    def test_rapid_engagement_pattern(self):
        """Test alternating quiz/quote pattern (rapid engagement)."""
        sequence_str = "quiz → quote → content → quiz → quote → content"
        result = SequenceParser.parse_sequence(sequence_str)
        
        assert result == ['quiz', 'quote', 'content', 'quiz', 'quote', 'content']
        assert SequenceParser.validate_sequence(result) is True
    
    def test_minimal_valid_sequence(self):
        """Test the smallest valid sequence."""
        sequence_str = "content → quiz → quote"
        result = SequenceParser.parse_sequence(sequence_str)
        
        assert result == ['content', 'quiz', 'quote']
        assert SequenceParser.validate_sequence(result) is True
    
    def test_maximal_valid_sequence(self):
        """Test the largest valid sequence."""
        sequence_str = "content → quiz → content → quote → content → quiz → content → quote"
        result = SequenceParser.parse_sequence(sequence_str)
        
        assert result == ['content', 'quiz', 'content', 'quote', 'content', 'quiz', 'content', 'quote']
        assert SequenceParser.validate_sequence(result) is True
        assert len(result) == 8  # Maximum allowed


class TestSequenceParserIntegration:
    """Test integration scenarios."""
    
    def test_parse_and_validate_workflow(self):
        """Test the typical parse → validate workflow."""
        test_sequences = [
            "content → quiz → quote",
            "quote → content → quiz → content → quiz → quote",
            "quiz → content → quote → content → quiz → content",
            "content → content → quiz → quote → content → quiz"
        ]
        
        for sequence_str in test_sequences:
            # Parse should succeed
            parsed = SequenceParser.parse_sequence(sequence_str)
            assert isinstance(parsed, list)
            assert len(parsed) >= 3
            
            # Validation should succeed
            assert SequenceParser.validate_sequence(parsed) is True
    
    def test_invalid_sequences_fail_gracefully(self):
        """Test that invalid sequences fail with clear error messages."""
        invalid_sequences = [
            ("content → quiz", "must have at least 3 items"),
            ("content → quiz → video", "Invalid item type 'video'"),
            ("content → content → content → content", "Missing: quiz, quote"),
            ("quiz → quiz → quote → quote", "Missing: content")
        ]
        
        for sequence_str, expected_error in invalid_sequences:
            with pytest.raises(ValueError, match=expected_error):
                parsed = SequenceParser.parse_sequence(sequence_str)
                SequenceParser.validate_sequence(parsed)