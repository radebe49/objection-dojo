"""
Pydantic models for Dealfu API contracts.

These models define the data structures for:
- ChatRequest: Incoming chat requests from frontend
- ChatResponse: Outgoing responses to frontend
- CerebrasResponse: Parsed responses from Cerebras API
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Sentiment(str, Enum):
    """Valid sentiment values from Cerebras AI response."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ChatRequest(BaseModel):
    """
    Request payload for the /chat endpoint.
    
    Attributes:
        session_id: UUID identifying the conversation session
        user_text: Transcribed speech from the user
        current_patience: Current patience meter value (0-100)
    """
    session_id: str = Field(..., description="UUID from frontend identifying the session")
    user_text: str = Field(..., description="Transcribed speech from the user")
    current_patience: int = Field(
        ...,
        ge=0,
        le=100,
        description="Current patience meter value (0-100)"
    )


class ChatResponse(BaseModel):
    """
    Response payload from the /chat endpoint.
    
    Attributes:
        ai_text: AI persona's response text
        patience_score: New patience value (0-100)
        deal_closed: Win condition flag
        audio_base64: MP3 audio encoded as base64
    """
    ai_text: str = Field(..., description="AI persona's response text")
    patience_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="New patience value (0-100)"
    )
    deal_closed: bool = Field(..., description="Win condition flag")
    audio_base64: str = Field(..., description="MP3 audio encoded as base64")


class SessionCreate(BaseModel):
    """
    Request payload for creating a new session.
    
    Attributes:
        session_id: UUID identifying the session
        user_id: Optional user ID for authenticated users
        patience_start: Starting patience value (default 50)
    """
    session_id: str = Field(..., description="UUID for the session")
    user_id: str | None = Field(None, description="Optional user ID")
    patience_start: int = Field(50, ge=0, le=100, description="Starting patience value")


class SessionEnd(BaseModel):
    """
    Request payload for ending a session.
    
    Attributes:
        session_id: UUID of the session to end
        patience_end: Final patience value
        deal_closed: Whether the deal was closed
        turns: Total turns taken
    """
    session_id: str = Field(..., description="Session ID to end")
    patience_end: int = Field(..., ge=0, le=100, description="Final patience value")
    deal_closed: bool = Field(..., description="Whether deal was closed")
    turns: int = Field(..., ge=0, description="Total turns taken")


class LeaderboardEntry(BaseModel):
    """
    Leaderboard entry data.
    
    Attributes:
        user_id: User identifier
        username: Display name
        wins: Total wins
        losses: Total losses
        total_sessions: Total sessions played
        best_turns_to_win: Best (lowest) turns to win
        avg_patience_end: Average final patience score
    """
    user_id: str = Field(..., description="User identifier")
    username: str | None = Field(None, description="Display name")
    wins: int = Field(0, ge=0, description="Total wins")
    losses: int = Field(0, ge=0, description="Total losses")
    total_sessions: int = Field(0, ge=0, description="Total sessions played")
    best_turns_to_win: int | None = Field(None, description="Best turns to win")
    avg_patience_end: int = Field(50, ge=0, le=100, description="Average final patience")


class CerebrasResponse(BaseModel):
    """
    Parsed response from Cerebras API.
    
    The Cerebras API is prompted to return JSON with this structure.
    
    Attributes:
        text: AI response text to be spoken
        sentiment: Sentiment classification for patience calculation
        deal_closed: Whether the AI has agreed to close the deal
    """
    text: str = Field(..., description="AI response text")
    sentiment: Sentiment = Field(..., description="Sentiment: positive, negative, or neutral")
    deal_closed: bool = Field(..., description="Whether the deal is closed")

    @field_validator("sentiment", mode="before")
    @classmethod
    def validate_sentiment(cls, v):
        """Ensure sentiment is a valid enum value."""
        if isinstance(v, str):
            v = v.lower()
            if v not in [s.value for s in Sentiment]:
                raise ValueError(f"sentiment must be one of: positive, negative, neutral")
        return v


def calculate_patience(current: int, sentiment: str) -> int:
    """
    Calculate new patience score based on AI sentiment.
    
    Args:
        current: Current patience score (0-100)
        sentiment: Sentiment value ("positive", "negative", or "neutral")
    
    Returns:
        New patience score clamped to 0-100 range.
        
    Calculation:
        - positive: +15 points
        - negative: -20 points
        - neutral: no change
    
    Requirements: 4.5
    """
    delta = {
        "positive": 15,
        "negative": -20,
        "neutral": 0
    }
    new_score = current + delta.get(sentiment.lower(), 0)
    return max(0, min(100, new_score))


# ==================== Session & Leaderboard Models (Vultr Integration) ====================

class SessionCreate(BaseModel):
    """Request to create a new game session."""
    session_id: str = Field(..., description="UUID for the session")
    user_id: Optional[str] = Field(None, description="Optional user ID for authenticated users")
    patience_start: int = Field(50, ge=0, le=100, description="Starting patience value")


class SessionEnd(BaseModel):
    """Request to end a game session."""
    session_id: str = Field(..., description="Session ID to end")
    user_id: Optional[str] = Field(None, description="User ID for leaderboard update")
    username: Optional[str] = Field(None, description="Display name for leaderboard")
    patience_end: int = Field(..., ge=0, le=100, description="Final patience value")
    deal_closed: bool = Field(..., description="Whether deal was closed")
    turns: int = Field(..., ge=0, description="Total turns taken")


class LeaderboardEntry(BaseModel):
    """Leaderboard entry for a player."""
    user_id: str = Field(..., description="User ID")
    username: Optional[str] = Field(None, description="Display name")
    wins: int = Field(0, description="Total wins")
    losses: int = Field(0, description="Total losses")
    total_sessions: int = Field(0, description="Total sessions played")
    best_turns_to_win: Optional[int] = Field(None, description="Best (lowest) turns to win")
    avg_patience_end: int = Field(50, description="Average final patience")
