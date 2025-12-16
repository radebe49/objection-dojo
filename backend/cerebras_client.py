"""
Cerebras API client for Dealfu.

Handles communication with Cerebras AI API for generating
"The Skeptic CTO" persona responses.

Requirements: 3.1, 10.1, 10.2, 10.3
"""

import json
import os
from typing import Optional

import httpx
from pydantic import ValidationError

from models import CerebrasResponse


# System prompt for "The Skeptic CTO" persona
SYSTEM_PROMPT = """You are "The Skeptic CTO" - a busy, skeptical technology executive evaluating a sales pitch. 

Your personality:
- Time-conscious and impatient with fluff
- Technically savvy - you see through buzzwords
- Respectful but direct
- You've heard every pitch before

Your job:
- Listen to the salesperson's pitch
- Respond with realistic objections OR agreement
- If genuinely convinced, you may agree to a meeting

ALWAYS respond with valid JSON in this exact format:
{
  "text": "Your spoken response here",
  "sentiment": "positive" | "negative" | "neutral",
  "deal_closed": true | false
}

Rules for sentiment:
- "positive": The pitch addressed your concerns well, you're warming up
- "negative": The pitch was weak, vague, or didn't answer your question
- "neutral": The pitch was okay but didn't move the needle

Rules for deal_closed:
- Set to true ONLY if you're genuinely convinced and ready to schedule a meeting
- This should be rare - you're a tough sell"""


class CerebrasClientError(Exception):
    """Base exception for Cerebras client errors."""
    pass


class CerebrasInvalidResponseError(CerebrasClientError):
    """Raised when Cerebras returns invalid JSON after retries."""
    pass


class CerebrasClient:
    """
    Async client for Cerebras API.
    
    Handles sending conversation context to Cerebras and parsing
    the structured JSON response.
    
    Requirements: 3.1, 10.1, 10.2, 10.3
    """
    
    DEFAULT_MODEL = "llama-3.3-70b"
    MAX_RETRIES = 2
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.cerebras.ai/v1",
        model: Optional[str] = None,
    ):
        """
        Initialize the Cerebras client.
        
        Args:
            api_key: Cerebras API key. Defaults to CEREBRAS_API_KEY env var.
            base_url: Base URL for Cerebras API.
            model: Model to use. Defaults to llama-4-scout-17b-16e-instruct.
        """
        self.api_key = api_key or os.getenv("CEREBRAS_API_KEY")
        if not self.api_key:
            raise ValueError("CEREBRAS_API_KEY is required")
        
        self.base_url = base_url
        self.model = model or self.DEFAULT_MODEL
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _build_messages(
        self,
        user_text: str,
        conversation_history: list[dict],
    ) -> list[dict]:
        """
        Build the messages array for the Cerebras API.
        
        Args:
            user_text: Current user message.
            conversation_history: Previous conversation messages.
        
        Returns:
            List of message dicts for the API.
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history
        for entry in conversation_history:
            messages.append({
                "role": entry.get("role", "user"),
                "content": entry.get("content", ""),
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_text})
        
        return messages
    
    def _parse_response(self, content: str) -> CerebrasResponse:
        """
        Parse and validate the JSON response from Cerebras.
        
        Args:
            content: Raw response content from Cerebras.
        
        Returns:
            Validated CerebrasResponse.
        
        Raises:
            ValueError: If JSON is invalid or doesn't match schema.
        """
        # Try to extract JSON from the response
        content = content.strip()
        
        # Handle case where response might be wrapped in markdown code blocks
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first and last lines (code block markers)
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith("```") and not in_block:
                    in_block = True
                    continue
                elif line.startswith("```") and in_block:
                    break
                elif in_block:
                    json_lines.append(line)
            content = "\n".join(json_lines)
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
        
        try:
            return CerebrasResponse(**data)
        except ValidationError as e:
            raise ValueError(f"Response validation failed: {e}")
    
    async def get_response(
        self,
        user_text: str,
        conversation_history: list[dict] | None = None,
    ) -> CerebrasResponse:
        """
        Get AI response for user input.
        
        Implements retry logic for invalid JSON responses (up to 2 retries).
        
        Args:
            user_text: User's transcribed speech.
            conversation_history: Previous conversation messages.
        
        Returns:
            Validated CerebrasResponse with text, sentiment, and deal_closed.
        
        Raises:
            CerebrasInvalidResponseError: If valid JSON not received after retries.
            CerebrasClientError: For other API errors.
        
        Requirements: 3.1, 10.1, 10.2, 10.3
        """
        if conversation_history is None:
            conversation_history = []
        
        messages = self._build_messages(user_text, conversation_history)
        client = await self._get_client()
        
        last_error: Optional[Exception] = None
        
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = await client.post(
                    "/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500,
                    },
                )
                response.raise_for_status()
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                return self._parse_response(content)
                
            except (ValueError, KeyError, IndexError) as e:
                last_error = e
                # Retry on parse errors
                if attempt < self.MAX_RETRIES:
                    continue
            except httpx.HTTPStatusError as e:
                raise CerebrasClientError(f"API request failed: {e}")
            except httpx.RequestError as e:
                raise CerebrasClientError(f"Network error: {e}")
        
        raise CerebrasInvalidResponseError(
            f"Failed to get valid JSON response after {self.MAX_RETRIES + 1} attempts. "
            f"Last error: {last_error}"
        )
