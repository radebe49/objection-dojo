"""
ElevenLabs API client for Dealfu.

Handles text-to-speech conversion using ElevenLabs API.

Requirements: 3.2, 3.3
"""

import os
from typing import Optional

import httpx


class ElevenLabsClientError(Exception):
    """Base exception for ElevenLabs client errors."""
    pass


class ElevenLabsClient:
    """
    Async client for ElevenLabs TTS API.
    
    Converts text to speech audio in MP3 format.
    
    Requirements: 3.2, 3.3
    """
    
    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        base_url: str = "https://api.elevenlabs.io/v1",
    ):
        """
        Initialize the ElevenLabs client.
        
        Args:
            api_key: ElevenLabs API key. Defaults to ELEVENLABS_API_KEY env var.
            voice_id: Voice ID to use. Defaults to ELEVENLABS_VOICE_ID env var or Rachel.
            base_url: Base URL for ElevenLabs API.
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is required")
        
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID") or self.DEFAULT_VOICE_ID
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "xi-api-key": self.api_key,
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
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech audio using turbo model for low latency.
        
        Args:
            text: Text to convert to speech.
        
        Returns:
            Raw MP3 audio bytes.
        
        Raises:
            ElevenLabsClientError: If API request fails.
        
        Requirements: 3.2, 3.3
        
        Performance: Uses eleven_turbo_v2_5 for ~40% faster generation
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        client = await self._get_client()
        
        try:
            response = await client.post(
                f"/text-to-speech/{self.voice_id}",
                json={
                    "text": text,
                    # Turbo model for low-latency conversational use
                    "model_id": "eleven_turbo_v2_5",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
                headers={
                    "Accept": "audio/mpeg",
                },
            )
            response.raise_for_status()
            
            return response.content
            
        except httpx.HTTPStatusError as e:
            raise ElevenLabsClientError(f"API request failed: {e}")
        except httpx.RequestError as e:
            raise ElevenLabsClientError(f"Network error: {e}")
