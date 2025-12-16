"""
LiquidMetal Raindrop SmartMemory client for Dealfu.

Handles session-based conversation context storage.

Requirements: 9.3, 9.4, 9.5
"""

import os
from datetime import datetime
from typing import Optional

import httpx


class SmartMemoryClientError(Exception):
    """Base exception for SmartMemory client errors."""
    pass


class SmartMemoryClient:
    """
    Client for LiquidMetal Raindrop SmartMemory.
    
    Manages conversation history storage per session.
    
    Requirements: 9.3, 9.4, 9.5
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the SmartMemory client.
        
        Args:
            api_key: Raindrop API key. Defaults to RAINDROP_API_KEY env var.
            base_url: Base URL for Raindrop API. Defaults to RAINDROP_BASE_URL env var.
        """
        self.api_key = api_key or os.getenv("RAINDROP_API_KEY")
        self.base_url = base_url or os.getenv("RAINDROP_BASE_URL", "https://api.raindrop.io/v1")
        self._client: Optional[httpx.AsyncClient] = None
        
        # In-memory fallback storage when API is not configured
        self._local_storage: dict[str, list[dict]] = {}
    
    @property
    def is_configured(self) -> bool:
        """Check if the client is configured with API credentials."""
        return bool(self.api_key)
    
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

    async def get_history(self, session_id: str) -> list[dict]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: UUID identifying the conversation session.
        
        Returns:
            List of conversation entries with role and content.
        
        Requirements: 9.3
        """
        if not session_id:
            raise ValueError("session_id is required")
        
        # Always use local in-memory storage for now
        # External SmartMemory API integration can be added later
        return self._local_storage.get(session_id, [])
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: UUID identifying the conversation session.
            role: Message role ("user" or "assistant").
            content: Message content.
        
        Requirements: 9.4, 9.5
        """
        if not session_id:
            raise ValueError("session_id is required")
        if not role:
            raise ValueError("role is required")
        if not content:
            raise ValueError("content is required")
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Always use local in-memory storage for now
        # External SmartMemory API integration can be added later
        if session_id not in self._local_storage:
            self._local_storage[session_id] = []
        self._local_storage[session_id].append(message)
    
    def clear_local_storage(self, session_id: Optional[str] = None) -> None:
        """
        Clear local storage (for testing purposes).
        
        Args:
            session_id: If provided, clear only that session. Otherwise clear all.
        """
        if session_id:
            self._local_storage.pop(session_id, None)
        else:
            self._local_storage.clear()
