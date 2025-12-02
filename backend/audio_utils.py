"""
Audio utility functions for Objection Dojo.

Provides base64 encoding/decoding for audio data.

Requirements: 3.4
"""

import base64


def encode_audio_base64(audio_bytes: bytes) -> str:
    """
    Encode audio bytes to base64 string.
    
    Args:
        audio_bytes: Raw audio data (e.g., MP3 bytes).
    
    Returns:
        Base64 encoded string.
    
    Requirements: 3.4
    """
    return base64.b64encode(audio_bytes).decode("utf-8")


def decode_audio_base64(audio_base64: str) -> bytes:
    """
    Decode base64 string to audio bytes.
    
    Args:
        audio_base64: Base64 encoded audio string.
    
    Returns:
        Raw audio bytes.
    
    Requirements: 3.4
    """
    return base64.b64decode(audio_base64.encode("utf-8"))
