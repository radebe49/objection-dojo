"""
LiquidMetal Raindrop SmartMemory client for Dealfu.

Integrates with Raindrop's SmartMemory API for session-based conversation context.
This is a REQUIRED integration for the AI Champion Ship hackathon.

API Base: https://api.raindrop.run/v1/
Auth: Bearer token (RAINDROP_API_KEY)

Requirements: Hackathon compliance - Raindrop Smart Components
"""

import os
from datetime import datetime
from typing import Optional
import httpx


class RaindropClientError(Exception):
    """Base exception for Raindrop client errors."""
    pass


class RaindropSmartMemoryClient:
    """
    Client for LiquidMetal Raindrop SmartMemory API.
    
    Uses Raindrop's SmartMemory Smart Component for session-based
    conversation context storage - required for hackathon compliance.
    
    SmartMemory provides:
    - Working Memory: Active session context
    - Episodic Memory: Historical session archives
    - Semantic Memory: Structured knowledge documents
    - Procedural Memory: Reusable templates/prompts
    """
    
    BASE_URL = "https://api.raindrop.run/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        app_name: str = "dealfu",
        memory_name: str = "conversation-memory",
        version: str = "1",
    ):
        """
        Initialize the Raindrop SmartMemory client.
        
        Args:
            api_key: Raindrop API key. Defaults to RAINDROP_API_KEY env var.
            app_name: Application name in Raindrop.
            memory_name: SmartMemory instance name.
            version: Application version.
        """
        self.api_key = api_key or os.getenv("RAINDROP_API_KEY")
        if not self.api_key:
            raise ValueError(
                "RAINDROP_API_KEY is required. "
                "Get your API key from https://liquidmetal.run"
            )
        
        self.app_name = app_name
        self.memory_name = memory_name
        self.version = version
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_smart_memory_location(self) -> dict:
        """Get the SmartMemory location object for API calls."""
        return {
            "smartMemory": {
                "name": self.memory_name,
                "application_name": self.app_name,
                "version": self.version
            }
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
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

    # ==================== Working Memory Methods ====================
    
    async def start_session(self) -> str:
        """
        Start a new working memory session.
        
        Returns:
            Session ID for the new session.
        """
        client = await self._get_client()
        
        try:
            response = await client.post(
                "/start_session",
                json={
                    "smart_memory_location": self._get_smart_memory_location()
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["sessionId"]
        except httpx.HTTPStatusError as e:
            raise RaindropClientError(f"Failed to start session: {e}")
        except httpx.RequestError as e:
            raise RaindropClientError(f"Network error: {e}")
    
    async def end_session(self, session_id: str, flush: bool = True) -> bool:
        """
        End a working memory session.
        
        Args:
            session_id: Session to end.
            flush: Whether to flush to episodic memory for long-term storage.
        
        Returns:
            True if successful.
        """
        client = await self._get_client()
        
        try:
            response = await client.post(
                "/end_session",
                json={
                    "smart_memory_location": self._get_smart_memory_location(),
                    "session_id": session_id,
                    "flush": flush
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except httpx.HTTPStatusError as e:
            raise RaindropClientError(f"Failed to end session: {e}")
        except httpx.RequestError as e:
            raise RaindropClientError(f"Network error: {e}")
    
    async def put_memory(
        self,
        session_id: str,
        content: str,
        timeline: str = "conversation",
        agent: str = "dealfu",
        key: Optional[str] = None,
    ) -> str:
        """
        Store a memory entry in working memory.
        
        Args:
            session_id: Session to store memory in.
            content: Memory content (message text).
            timeline: Timeline for organizing memories.
            agent: Agent identifier.
            key: Optional key for direct retrieval.
        
        Returns:
            Memory ID of the stored entry.
        """
        client = await self._get_client()
        
        payload = {
            "smart_memory_location": self._get_smart_memory_location(),
            "session_id": session_id,
            "content": content,
            "timeline": timeline,
            "agent": agent,
        }
        if key:
            payload["key"] = key
        
        try:
            response = await client.post("/put_memory", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["memoryId"]
        except httpx.HTTPStatusError as e:
            raise RaindropClientError(f"Failed to store memory: {e}")
        except httpx.RequestError as e:
            raise RaindropClientError(f"Network error: {e}")
    
    async def get_memory(
        self,
        session_id: str,
        n_most_recent: Optional[int] = None,
        timeline: str = "conversation",
    ) -> list[dict]:
        """
        Retrieve memories from working memory.
        
        Args:
            session_id: Session to retrieve from.
            n_most_recent: Limit to N most recent entries.
            timeline: Timeline to filter by.
        
        Returns:
            List of memory entries.
        """
        client = await self._get_client()
        
        payload = {
            "smart_memory_location": self._get_smart_memory_location(),
            "session_id": session_id,
            "timeline": timeline,
        }
        if n_most_recent:
            payload["nMostRecent"] = n_most_recent
        
        try:
            response = await client.post("/get_memory", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("memories", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []  # Session doesn't exist yet
            raise RaindropClientError(f"Failed to get memory: {e}")
        except httpx.RequestError as e:
            raise RaindropClientError(f"Network error: {e}")
    
    async def search_memory(
        self,
        session_id: str,
        terms: str,
        n_most_recent: int = 10,
    ) -> list[dict]:
        """
        Search working memory using semantic search.
        
        Args:
            session_id: Session to search in.
            terms: Natural language search query.
            n_most_recent: Max results to return.
        
        Returns:
            List of matching memory entries.
        """
        client = await self._get_client()
        
        try:
            response = await client.post(
                "/search_memory",
                json={
                    "smart_memory_location": self._get_smart_memory_location(),
                    "session_id": session_id,
                    "terms": terms,
                    "nMostRecent": n_most_recent,
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("memories", [])
        except httpx.HTTPStatusError as e:
            raise RaindropClientError(f"Failed to search memory: {e}")
        except httpx.RequestError as e:
            raise RaindropClientError(f"Network error: {e}")

    # ==================== Episodic Memory Methods ====================
    
    async def search_episodic_memory(
        self,
        terms: str,
        n_most_recent: int = 5,
    ) -> list[dict]:
        """
        Search historical sessions in episodic memory.
        
        Args:
            terms: Natural language search query.
            n_most_recent: Max results to return.
        
        Returns:
            List of matching session summaries.
        """
        client = await self._get_client()
        
        try:
            response = await client.post(
                "/search_episodic_memory",
                json={
                    "smart_memory_location": self._get_smart_memory_location(),
                    "terms": terms,
                    "nMostRecent": n_most_recent,
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("entries", [])
        except httpx.HTTPStatusError as e:
            raise RaindropClientError(f"Failed to search episodic memory: {e}")
        except httpx.RequestError as e:
            raise RaindropClientError(f"Network error: {e}")

    # ==================== Helper Methods for Conversation ====================
    
    async def add_user_message(self, session_id: str, content: str) -> str:
        """Add a user message to the conversation."""
        return await self.put_memory(
            session_id=session_id,
            content=f"[USER]: {content}",
            agent="user",
        )
    
    async def add_assistant_message(self, session_id: str, content: str) -> str:
        """Add an assistant message to the conversation."""
        return await self.put_memory(
            session_id=session_id,
            content=f"[ASSISTANT]: {content}",
            agent="skeptic-cto",
        )
    
    async def get_conversation_history(
        self,
        session_id: str,
        n_most_recent: int = 20,
    ) -> list[dict]:
        """
        Get conversation history formatted for LLM context.
        
        Returns list of {"role": "user"|"assistant", "content": "..."} dicts.
        """
        memories = await self.get_memory(
            session_id=session_id,
            n_most_recent=n_most_recent,
        )
        
        history = []
        for mem in memories:
            content = mem.get("content", "")
            if content.startswith("[USER]:"):
                history.append({
                    "role": "user",
                    "content": content.replace("[USER]: ", "")
                })
            elif content.startswith("[ASSISTANT]:"):
                history.append({
                    "role": "assistant", 
                    "content": content.replace("[ASSISTANT]: ", "")
                })
        
        return history
