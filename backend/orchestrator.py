"""
Orchestrator service for Objection Dojo.

Coordinates the flow: get history → call Cerebras → call ElevenLabs → 
encode audio → calculate patience → return consolidated response.

Requirements: 3.1, 3.2, 3.4, 3.5, 9.6
"""

import base64
from typing import Optional

from cerebras_client import CerebrasClient, CerebrasClientError
from elevenlabs_client import ElevenLabsClient, ElevenLabsClientError
from smartmemory_client import SmartMemoryClient, SmartMemoryClientError
from models import ChatRequest, ChatResponse, calculate_patience


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    pass


class OrchestratorService:
    """
    Orchestrates the chat flow for Objection Dojo.
    
    Coordinates:
    1. Get conversation history from SmartMemory
    2. Call Cerebras API with context
    3. Call ElevenLabs API for TTS
    4. Encode audio as base64
    5. Calculate new patience score
    6. Return consolidated ChatResponse
    
    Requirements: 3.1, 3.2, 3.4, 3.5, 9.6
    """
    
    def __init__(
        self,
        cerebras_client: Optional[CerebrasClient] = None,
        elevenlabs_client: Optional[ElevenLabsClient] = None,
        smartmemory_client: Optional[SmartMemoryClient] = None,
    ):
        """
        Initialize the orchestrator with API clients.
        
        Args:
            cerebras_client: Client for Cerebras API. Created if not provided.
            elevenlabs_client: Client for ElevenLabs API. Created if not provided.
            smartmemory_client: Client for SmartMemory. Created if not provided.
        """
        self.cerebras_client = cerebras_client or CerebrasClient()
        self.elevenlabs_client = elevenlabs_client or ElevenLabsClient()
        self.smartmemory_client = smartmemory_client or SmartMemoryClient()
    
    async def close(self):
        """Close all API clients."""
        await self.cerebras_client.close()
        await self.elevenlabs_client.close()
        await self.smartmemory_client.close()
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request through the full pipeline.
        
        Flow:
        1. Get conversation history from SmartMemory (Req 9.6)
        2. Call Cerebras with user text and history (Req 3.1)
        3. Store user message in SmartMemory (Req 9.4)
        4. Call ElevenLabs for TTS (Req 3.2)
        5. Encode audio as base64 (Req 3.4)
        6. Calculate new patience score
        7. Store AI response in SmartMemory (Req 9.5)
        8. Return consolidated response (Req 3.5)
        
        Args:
            request: ChatRequest with session_id, user_text, current_patience.
        
        Returns:
            ChatResponse with ai_text, patience_score, deal_closed, audio_base64.
        
        Raises:
            OrchestratorError: If any step in the pipeline fails.
        """
        try:
            # Step 1: Get conversation history (Req 9.6)
            history = await self.smartmemory_client.get_history(request.session_id)
            
            # Step 2: Call Cerebras with context (Req 3.1)
            cerebras_response = await self.cerebras_client.get_response(
                user_text=request.user_text,
                conversation_history=history,
            )
            
            # Step 3: Store user message (Req 9.4)
            await self.smartmemory_client.add_message(
                session_id=request.session_id,
                role="user",
                content=request.user_text,
            )
            
            # Step 4: Call ElevenLabs for TTS (Req 3.2, 3.3)
            audio_bytes = await self.elevenlabs_client.text_to_speech(
                text=cerebras_response.text
            )
            
            # Step 5: Encode audio as base64 (Req 3.4)
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            # Step 6: Calculate new patience score
            new_patience = calculate_patience(
                current=request.current_patience,
                sentiment=cerebras_response.sentiment.value,
            )
            
            # Step 7: Store AI response (Req 9.5)
            await self.smartmemory_client.add_message(
                session_id=request.session_id,
                role="assistant",
                content=cerebras_response.text,
            )
            
            # Step 8: Return consolidated response (Req 3.5)
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
        except SmartMemoryClientError as e:
            raise OrchestratorError(f"SmartMemory error: {e}")
        except Exception as e:
            raise OrchestratorError(f"Unexpected error: {e}")
