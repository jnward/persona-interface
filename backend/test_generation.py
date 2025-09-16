#!/usr/bin/env python3
"""
Test suite for the generation module, particularly format_messages_for_chat.
"""

import pytest
from transformers import AutoTokenizer
from generation import format_messages_for_chat


@pytest.fixture
def tokenizer():
    """Load the tokenizer once for all tests."""
    return AutoTokenizer.from_pretrained("google/gemma-3-12b-it")


class TestFormatMessagesForChat:
    """Test cases for format_messages_for_chat function."""

    def test_basic_user_message(self, tokenizer):
        """Test formatting a simple user message."""
        messages = [{"role": "user", "content": "Hello"}]

        # Normal formatting (not partial)
        result = format_messages_for_chat(tokenizer, messages, is_partial=False)

        assert "<start_of_turn>user" in result
        assert "Hello" in result
        assert "<end_of_turn>" in result
        assert result.endswith("<start_of_turn>model\n")

    def test_user_assistant_conversation(self, tokenizer):
        """Test formatting a full conversation."""
        messages = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello there"}
        ]

        result = format_messages_for_chat(tokenizer, messages, is_partial=False)

        assert "Hi" in result
        assert "Hello there" in result
        # Should end with new model turn
        assert result.endswith("<start_of_turn>model\n")

    def test_partial_assistant_no_trailing_space(self, tokenizer):
        """Test is_partial with assistant message without trailing space."""
        messages = [
            {"role": "user", "content": "Count:"},
            {"role": "assistant", "content": "1, 2"}
        ]

        result = format_messages_for_chat(tokenizer, messages, is_partial=True)

        # Should use continue_final_message format (no closing tag)
        assert not result.endswith("<start_of_turn>model\n")
        assert result.endswith("1, 2")  # Content should be preserved
        # Check that the assistant message is not closed (no end_of_turn after "1, 2")
        assert not result.endswith("1, 2<end_of_turn>")

    def test_partial_assistant_with_single_trailing_space(self, tokenizer):
        """Test is_partial preserves single trailing space."""
        messages = [
            {"role": "user", "content": "Count:"},
            {"role": "assistant", "content": "1, "}
        ]

        result = format_messages_for_chat(tokenizer, messages, is_partial=True)

        # The critical test: trailing space should be preserved
        assert result.endswith("1, "), f"Expected trailing space, got: {repr(result[-10:])}"
        assert not result.endswith("<start_of_turn>model\n")

    def test_partial_assistant_with_multiple_trailing_spaces(self, tokenizer):
        """Test is_partial preserves multiple trailing spaces."""
        messages = [
            {"role": "user", "content": "Test:"},
            {"role": "assistant", "content": "Hello   "}
        ]

        result = format_messages_for_chat(tokenizer, messages, is_partial=True)

        # Should preserve all three trailing spaces
        assert result.endswith("Hello   "), f"Expected 3 trailing spaces, got: {repr(result[-15:])}"

    def test_partial_assistant_with_newline(self, tokenizer):
        """Test is_partial with trailing newline."""
        messages = [
            {"role": "user", "content": "Test:"},
            {"role": "assistant", "content": "Line1\n"}
        ]

        result = format_messages_for_chat(tokenizer, messages, is_partial=True)

        # Should preserve the newline
        assert result.endswith("Line1\n"), f"Expected trailing newline, got: {repr(result[-10:])}"

    def test_partial_assistant_with_mixed_whitespace(self, tokenizer):
        """Test is_partial with mixed trailing whitespace."""
        messages = [
            {"role": "user", "content": "Test:"},
            {"role": "assistant", "content": "Text \t\n "}
        ]

        result = format_messages_for_chat(tokenizer, messages, is_partial=True)

        # Should preserve all trailing whitespace
        assert result.endswith("Text \t\n "), f"Expected trailing whitespace, got: {repr(result[-15:])}"

    def test_partial_only_affects_assistant(self, tokenizer):
        """Test that is_partial only affects assistant messages."""
        messages = [
            {"role": "user", "content": "Hello "}  # User with trailing space
        ]

        # is_partial should not affect user messages
        result_normal = format_messages_for_chat(tokenizer, messages, is_partial=False)
        result_partial = format_messages_for_chat(tokenizer, messages, is_partial=True)

        # Both should be the same (is_partial only affects assistant messages)
        assert result_normal == result_partial

    def test_empty_assistant_content(self, tokenizer):
        """Test handling of empty assistant content."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": ""}
        ]

        # Should not crash on empty content
        result = format_messages_for_chat(tokenizer, messages, is_partial=True)
        assert result  # Should return something valid

    def test_normal_vs_partial_format_difference(self, tokenizer):
        """Test the key difference between normal and partial formatting."""
        messages = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"}
        ]

        normal = format_messages_for_chat(tokenizer, messages, is_partial=False)
        partial = format_messages_for_chat(tokenizer, messages, is_partial=True)

        # Normal should close the assistant turn and start a new one
        assert normal.endswith("<start_of_turn>model\n")

        # Partial should leave the assistant turn open
        assert partial.endswith("Hello")
        assert not partial.endswith("<start_of_turn>model\n")

    def test_tokenization_preserves_spaces(self, tokenizer):
        """Verify that tokenization preserves the spaces we add back."""
        messages = [
            {"role": "user", "content": "Count:"},
            {"role": "assistant", "content": "1, "}
        ]

        formatted = format_messages_for_chat(tokenizer, messages, is_partial=True)

        # Tokenize and decode to verify round-trip
        tokens = tokenizer(formatted, return_tensors="pt")
        decoded = tokenizer.decode(tokens["input_ids"][0], skip_special_tokens=False)

        # The decoded version should still have the trailing space
        assert decoded.endswith("1, "), f"Space lost in tokenization: {repr(decoded[-10:])}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])