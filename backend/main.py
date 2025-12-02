from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse
from orchestrator import OrchestratorService, OrchestratorError

load_dotenv()

# Global orchestrator instance
orchestrator: OrchestratorService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - initialize and cleanup resources."""
    global orchestrator
    orchestrator = OrchestratorService()
    yield
    if orchestrator:
        await orchestrator.close()


app = FastAPI(
    title="Objection Dojo API",
    description="Backend API for the Objection Dojo sales simulation",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production domain if configured
production_domain = os.getenv("PRODUCTION_DOMAIN")
if production_domain:
    origins.append(production_domain)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Objection Dojo API", "status": "healthy"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return AI response with audio.
    
    Accepts ChatRequest with session_id, user_text, current_patience.
    Returns ChatResponse with ai_text, patience_score, deal_closed, audio_base64.
    
    Requirements: 3.5, 9.2, 9.3
    """
    global orchestrator
    
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Service not initialized"
        )
    
    try:
        response = await orchestrator.process_chat(request)
        return response
    except OrchestratorError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
