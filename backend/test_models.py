"""
Property-based tests for Dealfu models.

Uses Hypothesis for property-based testing to verify model validation
across a wide range of inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError

from models import CerebrasResponse, Sentiment


# **Feature: dealfu, Property 10: Cerebras Response Validation**
# **Validates: Requirements 10.2, 10.4, 10.5**
#
# *For any* JSON object, validation SHALL pass if and only if it contains:
# - "text" field with string value
# - "sentiment" field with value in ["positive", "negative", "neutral"]
# - "deal_closed" field with boolean value


# Strategy for valid sentiment values
valid_sentiments = st.sampled_from(["positive", "negative", "neutral"])

# Strategy for valid CerebrasResponse data
valid_cerebras_data = st.fixed_dictionaries({
    "text": st.text(min_size=1),
    "sentiment": valid_sentiments,
    "deal_closed": st.booleans(),
})


@settings(max_examples=100)
@given(data=valid_cerebras_data)
def test_valid_cerebras_response_passes_validation(data):
    """
    **Feature: dealfu, Property 10: Cerebras Response Validation**
    
    Property: For any valid JSON with correct fields and types,
    validation SHALL pass.
    
    **Validates: Requirements 10.2, 10.4, 10.5**
    """
    response = CerebrasResponse(**data)
    
    assert response.text == data["text"]
    assert response.sentiment.value == data["sentiment"]
    assert response.deal_closed == data["deal_closed"]


@settings(max_examples=100)
@given(
    text=st.text(min_size=1),
    deal_closed=st.booleans(),
    invalid_sentiment=st.text().filter(
        lambda s: s.lower() not in ["positive", "negative", "neutral"]
    )
)
def test_invalid_sentiment_fails_validation(text, deal_closed, invalid_sentiment):
    """
    **Feature: dealfu, Property 10: Cerebras Response Validation**
    
    Property: For any JSON with invalid sentiment value,
    validation SHALL fail.
    
    **Validates: Requirements 10.4**
    """
    data = {
        "text": text,
        "sentiment": invalid_sentiment,
        "deal_closed": deal_closed,
    }
    
    with pytest.raises(ValidationError):
        CerebrasResponse(**data)


@settings(max_examples=100)
@given(
    sentiment=valid_sentiments,
    deal_closed=st.booleans(),
)
def test_missing_text_field_fails_validation(sentiment, deal_closed):
    """
    **Feature: dealfu, Property 10: Cerebras Response Validation**
    
    Property: For any JSON missing the "text" field,
    validation SHALL fail.
    
    **Validates: Requirements 10.2**
    """
    data = {
        "sentiment": sentiment,
        "deal_closed": deal_closed,
    }
    
    with pytest.raises(ValidationError):
        CerebrasResponse(**data)


@settings(max_examples=100)
@given(
    text=st.text(min_size=1),
    deal_closed=st.booleans(),
)
def test_missing_sentiment_field_fails_validation(text, deal_closed):
    """
    **Feature: dealfu, Property 10: Cerebras Response Validation**
    
    Property: For any JSON missing the "sentiment" field,
    validation SHALL fail.
    
    **Validates: Requirements 10.4**
    """
    data = {
        "text": text,
        "deal_closed": deal_closed,
    }
    
    with pytest.raises(ValidationError):
        CerebrasResponse(**data)


@settings(max_examples=100)
@given(
    text=st.text(min_size=1),
    sentiment=valid_sentiments,
)
def test_missing_deal_closed_field_fails_validation(text, sentiment):
    """
    **Feature: dealfu, Property 10: Cerebras Response Validation**
    
    Property: For any JSON missing the "deal_closed" field,
    validation SHALL fail.
    
    **Validates: Requirements 10.5**
    """
    data = {
        "text": text,
        "sentiment": sentiment,
    }
    
    with pytest.raises(ValidationError):
        CerebrasResponse(**data)


@settings(max_examples=100)
@given(data=valid_cerebras_data)
def test_deal_closed_is_always_boolean(data):
    """
    **Feature: dealfu, Property 10: Cerebras Response Validation**
    
    Property: For any valid CerebrasResponse, the deal_closed field
    SHALL be a boolean value.
    
    **Validates: Requirements 10.5**
    """
    response = CerebrasResponse(**data)
    assert isinstance(response.deal_closed, bool)


# **Feature: dealfu, Property 5: Patience Score Calculation**
# **Validates: Requirements 4.5**
#
# *For any* starting patience score (0-100) and sentiment value, the new score SHALL equal:
# - current + 15 if sentiment is "positive"
# - current - 20 if sentiment is "negative"
# - current + 0 if sentiment is "neutral"
# And the result SHALL be clamped to the range [0, 100].

from models import calculate_patience


# Strategy for valid patience scores (0-100)
valid_patience_scores = st.integers(min_value=0, max_value=100)


@settings(max_examples=100)
@given(
    current_patience=valid_patience_scores,
    sentiment=valid_sentiments,
)
def test_patience_calculation_applies_correct_formula(current_patience, sentiment):
    """
    **Feature: dealfu, Property 5: Patience Score Calculation**
    
    Property: For any starting score and sentiment, the formula is correctly applied:
    - positive: +15 points
    - negative: -20 points
    - neutral: no change
    And the result is clamped to [0, 100].
    
    **Validates: Requirements 4.5**
    """
    expected_delta = {
        "positive": 15,
        "negative": -20,
        "neutral": 0
    }
    
    result = calculate_patience(current_patience, sentiment)
    
    # Calculate expected value with clamping
    expected_raw = current_patience + expected_delta[sentiment]
    expected_clamped = max(0, min(100, expected_raw))
    
    assert result == expected_clamped


@settings(max_examples=100)
@given(
    current_patience=valid_patience_scores,
    sentiment=valid_sentiments,
)
def test_patience_score_always_in_valid_range(current_patience, sentiment):
    """
    **Feature: dealfu, Property 5: Patience Score Calculation**
    
    Property: For any input, the result SHALL always be in the range [0, 100].
    
    **Validates: Requirements 4.5**
    """
    result = calculate_patience(current_patience, sentiment)
    
    assert 0 <= result <= 100


@settings(max_examples=100)
@given(current_patience=valid_patience_scores)
def test_positive_sentiment_increases_patience(current_patience):
    """
    **Feature: dealfu, Property 5: Patience Score Calculation**
    
    Property: Positive sentiment SHALL increase patience by 15 (before clamping).
    
    **Validates: Requirements 4.5**
    """
    result = calculate_patience(current_patience, "positive")
    
    # If not at max, should increase by 15 (clamped to 100)
    expected = min(100, current_patience + 15)
    assert result == expected


@settings(max_examples=100)
@given(current_patience=valid_patience_scores)
def test_negative_sentiment_decreases_patience(current_patience):
    """
    **Feature: dealfu, Property 5: Patience Score Calculation**
    
    Property: Negative sentiment SHALL decrease patience by 20 (before clamping).
    
    **Validates: Requirements 4.5**
    """
    result = calculate_patience(current_patience, "negative")
    
    # Should decrease by 20 (clamped to 0)
    expected = max(0, current_patience - 20)
    assert result == expected


@settings(max_examples=100)
@given(current_patience=valid_patience_scores)
def test_neutral_sentiment_preserves_patience(current_patience):
    """
    **Feature: dealfu, Property 5: Patience Score Calculation**
    
    Property: Neutral sentiment SHALL not change the patience score.
    
    **Validates: Requirements 4.5**
    """
    result = calculate_patience(current_patience, "neutral")
    
    assert result == current_patience


# **Feature: dealfu, Property 3: Base64 Audio Round-Trip**
# **Validates: Requirements 3.4**
#
# *For any* valid MP3 binary data, encoding to base64 and then decoding
# SHALL produce the original binary data.

from audio_utils import encode_audio_base64, decode_audio_base64


@settings(max_examples=100)
@given(audio_data=st.binary(min_size=1, max_size=10000))
def test_base64_audio_round_trip(audio_data):
    """
    **Feature: dealfu, Property 3: Base64 Audio Round-Trip**
    
    Property: For any binary data, encoding to base64 and then decoding
    SHALL produce the original binary data.
    
    **Validates: Requirements 3.4**
    """
    # Encode to base64
    encoded = encode_audio_base64(audio_data)
    
    # Verify encoded is a string
    assert isinstance(encoded, str)
    
    # Decode back to bytes
    decoded = decode_audio_base64(encoded)
    
    # Verify round-trip produces original data
    assert decoded == audio_data


@settings(max_examples=100)
@given(audio_data=st.binary(min_size=1, max_size=10000))
def test_base64_encoding_produces_valid_string(audio_data):
    """
    **Feature: dealfu, Property 3: Base64 Audio Round-Trip**
    
    Property: For any binary data, base64 encoding SHALL produce
    a valid ASCII string containing only base64 characters.
    
    **Validates: Requirements 3.4**
    """
    encoded = encode_audio_base64(audio_data)
    
    # Base64 alphabet plus padding character
    valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    
    # All characters should be valid base64 characters
    assert all(c in valid_chars for c in encoded)


# **Feature: dealfu, Property 4: Response Structure Completeness**
# **Validates: Requirements 3.5**
#
# *For any* successful backend response, the JSON SHALL contain all required fields:
# - ai_text (string)
# - patience_score (number 0-100)
# - deal_closed (boolean)
# - audio_base64 (string)

from models import ChatResponse


# Strategy for valid ChatResponse data
valid_chat_response_data = st.fixed_dictionaries({
    "ai_text": st.text(min_size=1),
    "patience_score": st.integers(min_value=0, max_value=100),
    "deal_closed": st.booleans(),
    "audio_base64": st.text(min_size=1),
})


@settings(max_examples=100)
@given(data=valid_chat_response_data)
def test_chat_response_contains_all_required_fields(data):
    """
    **Feature: dealfu, Property 4: Response Structure Completeness**
    
    Property: For any valid ChatResponse, all required fields SHALL be present
    with correct types: ai_text (string), patience_score (number 0-100),
    deal_closed (boolean), audio_base64 (string).
    
    **Validates: Requirements 3.5**
    """
    response = ChatResponse(**data)
    
    # Verify all required fields are present and have correct types
    assert hasattr(response, "ai_text")
    assert hasattr(response, "patience_score")
    assert hasattr(response, "deal_closed")
    assert hasattr(response, "audio_base64")
    
    # Verify types
    assert isinstance(response.ai_text, str)
    assert isinstance(response.patience_score, int)
    assert isinstance(response.deal_closed, bool)
    assert isinstance(response.audio_base64, str)
    
    # Verify values match input
    assert response.ai_text == data["ai_text"]
    assert response.patience_score == data["patience_score"]
    assert response.deal_closed == data["deal_closed"]
    assert response.audio_base64 == data["audio_base64"]


@settings(max_examples=100)
@given(data=valid_chat_response_data)
def test_chat_response_patience_score_in_valid_range(data):
    """
    **Feature: dealfu, Property 4: Response Structure Completeness**
    
    Property: For any ChatResponse, patience_score SHALL be in range [0, 100].
    
    **Validates: Requirements 3.5**
    """
    response = ChatResponse(**data)
    
    assert 0 <= response.patience_score <= 100


@settings(max_examples=100)
@given(
    ai_text=st.text(min_size=1),
    deal_closed=st.booleans(),
    audio_base64=st.text(min_size=1),
)
def test_chat_response_missing_patience_score_fails(ai_text, deal_closed, audio_base64):
    """
    **Feature: dealfu, Property 4: Response Structure Completeness**
    
    Property: For any JSON missing patience_score, validation SHALL fail.
    
    **Validates: Requirements 3.5**
    """
    data = {
        "ai_text": ai_text,
        "deal_closed": deal_closed,
        "audio_base64": audio_base64,
    }
    
    with pytest.raises(ValidationError):
        ChatResponse(**data)


@settings(max_examples=100)
@given(
    patience_score=st.integers(min_value=0, max_value=100),
    deal_closed=st.booleans(),
    audio_base64=st.text(min_size=1),
)
def test_chat_response_missing_ai_text_fails(patience_score, deal_closed, audio_base64):
    """
    **Feature: dealfu, Property 4: Response Structure Completeness**
    
    Property: For any JSON missing ai_text, validation SHALL fail.
    
    **Validates: Requirements 3.5**
    """
    data = {
        "patience_score": patience_score,
        "deal_closed": deal_closed,
        "audio_base64": audio_base64,
    }
    
    with pytest.raises(ValidationError):
        ChatResponse(**data)


@settings(max_examples=100)
@given(
    ai_text=st.text(min_size=1),
    patience_score=st.integers(min_value=0, max_value=100),
    audio_base64=st.text(min_size=1),
)
def test_chat_response_missing_deal_closed_fails(ai_text, patience_score, audio_base64):
    """
    **Feature: dealfu, Property 4: Response Structure Completeness**
    
    Property: For any JSON missing deal_closed, validation SHALL fail.
    
    **Validates: Requirements 3.5**
    """
    data = {
        "ai_text": ai_text,
        "patience_score": patience_score,
        "audio_base64": audio_base64,
    }
    
    with pytest.raises(ValidationError):
        ChatResponse(**data)


@settings(max_examples=100)
@given(
    ai_text=st.text(min_size=1),
    patience_score=st.integers(min_value=0, max_value=100),
    deal_closed=st.booleans(),
)
def test_chat_response_missing_audio_base64_fails(ai_text, patience_score, deal_closed):
    """
    **Feature: dealfu, Property 4: Response Structure Completeness**
    
    Property: For any JSON missing audio_base64, validation SHALL fail.
    
    **Validates: Requirements 3.5**
    """
    data = {
        "ai_text": ai_text,
        "patience_score": patience_score,
        "deal_closed": deal_closed,
    }
    
    with pytest.raises(ValidationError):
        ChatResponse(**data)


@settings(max_examples=100)
@given(
    ai_text=st.text(min_size=1),
    deal_closed=st.booleans(),
    audio_base64=st.text(min_size=1),
    invalid_patience=st.integers().filter(lambda x: x < 0 or x > 100),
)
def test_chat_response_invalid_patience_score_fails(ai_text, deal_closed, audio_base64, invalid_patience):
    """
    **Feature: dealfu, Property 4: Response Structure Completeness**
    
    Property: For any JSON with patience_score outside [0, 100], validation SHALL fail.
    
    **Validates: Requirements 3.5**
    """
    data = {
        "ai_text": ai_text,
        "patience_score": invalid_patience,
        "deal_closed": deal_closed,
        "audio_base64": audio_base64,
    }
    
    with pytest.raises(ValidationError):
        ChatResponse(**data)
