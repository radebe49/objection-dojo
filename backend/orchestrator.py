"""
Orchestrator service for Dealfu.

Coordinates the flow: get history → call Cerebras → call ElevenLabs → 
encode audio → calculate patience → return consolidated response.

Optimized for low-latency conversational experience using parallel processing.

Requirements: 3.1, 3.2, 3.4, 3.5, 9.6
Hackathon: Raindrop SmartMemory integration for AI Champion Ship
"""

import asyncio
import base64
import os
from typing import Optional

from cerebras_client import CerebrasClient, CerebrasClientError
from elevenlabs_client import ElevenLabsClient, ElevenLabsClientError
from smartmemory_client import SmartMemoryClient, SmartMemoryClientError
from models import ChatRequest, ChatResponse, calculate_patience

# Import Raindrop client for hackathon compliance
try:
    from raindrop_client import RaindropSmartMemoryClient, RaindropClientError
    RAINDROP_AVAILABLE = True
except ImportError:
    RAINDROP_AVAILABLE = False
    RaindropClientError = Exception


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    pass


class OrchestratorService:
    """
    Orchestrates the chat flow for Dealfu.
    
    Coordinates:
    1. Get conversation history from Raindrop SmartMemory (or local fallback)
    2. Call Cerebras API with context
    3. Call ElevenLabs API for TTS
    4. Encode audio as base64
    5. Calculate new patience score
    6. Return consolidated ChatResponse
    
    Requirements: 3.1, 3.2, 3.4, 3.5, 9.6
    Hackathon: Uses Raindrop SmartMemory when RAINDROP_API_KEY is set
    """
    
    def __init__(
        self,
        cerebras_client: Optional[CerebrasClient] = None,
        elevenlabs_client: Optional[ElevenLabsClient] = None,
        smartmemory_client: Optional[SmartMemoryClient] = None,
        raindrop_client: Optional["RaindropSmartMemoryClient"] = None,
    ):
        """
        Initialize the orchestrator with API clients.
        
        Args:
            cerebras_client: Client for Cerebras API. Created if not provided.
            elevenlabs_client: Client for ElevenLabs API. Created if not provided.
            smartmemory_client: Local fallback for SmartMemory.
            raindrop_client: Raindrop SmartMemory client (hackathon requirement).
        """
        self.cerebras_client = cerebras_client or CerebrasClient()
        self.elevenlabs_client = elevenlabs_client or ElevenLabsClient()
        
        # Use Raindrop SmartMemory if API key is configured (hackathon requirement)
        self.use_raindrop = RAINDROP_AVAILABLE and bool(os.getenv("RAINDROP_API_KEY"))
        
        if self.use_raindrop:
            self.raindrop_client = raindrop_client or RaindropSmartMemoryClient()
            self.smartmemory_client = None
            print("✅ Using Raindrop SmartMemory (hackathon compliant)")
        else:
            self.raindrop_client = None
            self.smartmemory_client = smartmemory_client or SmartMemoryClient()
            print("⚠️  Using local memory (set RAINDROP_API_KEY for hackathon)")
    
    async def close(self):
        """Close all API clients."""
        await self.cerebras_client.close()
        await self.elevenlabs_client.close()
        if self.raindrop_client:
            await self.raindrop_client.close()
        if self.smartmemory_client:
            await self.smartmemory_client.close()
    
    async def _get_history(self, session_id: str) -> list[dict]:
        """Get conversation history from Raindrop or local storage."""
        if self.use_raindrop and self.raindrop_client:
            try:
                return await self.raindrop_client.get_conversation_history(session_id)
            except Exception as e:
                # Gracefully fall back to empty history if Raindrop fails
                print(f"⚠️  Raindrop get_history failed, continuing without history: {e}")
                return []
        elif self.smartmemory_client:
            return await self.smartmemory_client.get_history(session_id)
        return []
    
    async def _store_messages(
        self, 
        session_id: str, 
        user_text: str, 
        ai_text: str
    ) -> None:
        """Store user and AI messages in memory."""
        if self.use_raindrop and self.raindrop_client:
            try:
                # Store in Raindrop SmartMemory (parallel)
                await asyncio.gather(
                    self.raindrop_client.add_user_message(session_id, user_text),
                    self.raindrop_client.add_assistant_message(session_id, ai_text),
                )
            except Exception as e:
                # Non-critical - don't fail the request if storage fails
                print(f"⚠️  Raindrop store_messages failed, continuing: {e}")
        elif self.smartmemory_client:
            # Store in local memory (parallel)
            await asyncio.gather(
                self.smartmemory_client.add_message(session_id, "user", user_text),
                self.smartmemory_client.add_message(session_id, "assistant", ai_text),
            )
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request through the full pipeline.
        
        Flow:
        1. Get conversation history from Raindrop SmartMemory (Req 9.6)
        2. Call Cerebras with user text and history (Req 3.1)
        3. Run TTS and message storage in PARALLEL for lower latency
        4. Encode audio as base64 (Req 3.4)
        5. Calculate new patience score
        6. Return consolidated response (Req 3.5)
        
        Args:
            request: ChatRequest with session_id, user_text, current_patience.
        
        Returns:
            ChatResponse with ai_text, patience_score, deal_closed, audio_base64.
        
        Raises:
            OrchestratorError: If any step in the pipeline fails.
        """
        try:
            # Step 1: Get conversation history (Req 9.6)
            history = await self._get_history(request.session_id)
            
            # Step 2: Call Cerebras with context (Req 3.1)
            cerebras_response = await self.cerebras_client.get_response(
                user_text=request.user_text,
                conversation_history=history,
            )
            
            # Step 3: Run TTS and message storage in PARALLEL for lower latency
            # This saves ~100-200ms by not waiting for storage operations
            tts_task = asyncio.create_task(
                self.elevenlabs_client.text_to_speech(text=cerebras_response.text)
            )
            storage_task = asyncio.create_task(
                self._store_messages(
                    session_id=request.session_id,
                    user_text=request.user_text,
                    ai_text=cerebras_response.text,
                )
            )
            
            # Wait for all parallel tasks - TTS is the critical path
            audio_bytes, _ = await asyncio.gather(tts_task, storage_task)
            
            # Step 4: Encode audio as base64 (Req 3.4)
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            # Step 5: Calculate new patience score
            new_patience = calculate_patience(
                current=request.current_patience,
                sentiment=cerebras_response.sentiment.value,
            )
            
            # Step 6: Return consolidated response (Req 3.5)
            return ChatResponse(
                ai_text=cerebras_response.text,
                patience_score=new_patience,
                deal_closed=cerebras_response.deal_closed,
                audio_base64=audio_base64,
            )
            
        except CerebrasClientError as e:
            raise OrchestratorError(f"Cerebras API error: {e}")
        except ElevenLabsClientError as e:
            raise OrchestratorError(f"ElevenLabs API error: {e}")
        except RaindropClientError as e:
            raise OrchestratorError(f"Raindrop SmartMemory error: {e}")
        except SmartMemoryClientError as e:
            raise OrchestratorError(f"SmartMemory error: {e}")
        except Exception as e:
            raise OrchestratorError(f"Unexpected error: {e}")
