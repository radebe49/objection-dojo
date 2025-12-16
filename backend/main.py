from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse, SessionCreate, SessionEnd, LeaderboardEntry
from orchestrator import OrchestratorService, OrchestratorError

# Import database client for Vultr integration (hackathon requirement)
try:
    from database import get_database_client, init_database, DatabaseClientError
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    get_database_client = lambda: None
    init_database = None

load_dotenv()

# Global instances
orchestrator: OrchestratorService | None = None
db_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - initialize and cleanup resources."""
    global orchestrator, db_client
    
    orchestrator = OrchestratorService()
    
    # Initialize Vultr PostgreSQL if configured (hackathon requirement)
    db_client = get_database_client()
    if db_client and init_database:
        try:
            await init_database()
            print("✅ Using Vultr PostgreSQL (hackathon compliant)")
        except Exception as e:
            print(f"⚠️  Vultr PostgreSQL not available: {e}")
            db_client = None
    else:
        print("⚠️  Vultr PostgreSQL not configured (set VULTR_DATABASE_URL)")
    
    yield
    
    if orchestrator:
        await orchestrator.close()


app = FastAPI(
    title="Dealfu API",
    description="Backend API for the Dealfu sales simulation",
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
    return {"message": "Dealfu API", "status": "healthy"}


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
    global orchestrator, db_client
    
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Service not initialized"
        )
    
    try:
        response = await orchestrator.process_chat(request)
        
        # Track turn in Vultr PostgreSQL if available
        if db_client:
            try:
                await db_client.update_session_turn(request.session_id)
            except Exception:
                pass  # Non-critical, don't fail the request
        
        return response
    except OrchestratorError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================== Session Endpoints (Vultr Integration) ====================

@app.post("/session/start")
async def start_session(request: SessionCreate):
    """
    Start a new game session.
    
    Tracks session in Vultr PostgreSQL for analytics and leaderboard.
    """
    global db_client
    
    if db_client:
        try:
            session = await db_client.create_session(
                session_id=request.session_id,
                user_id=request.user_id,
                patience_start=request.patience_start
            )
            return {"success": True, "session": session}
        except Exception as e:
            # Non-critical - return success anyway
            return {"success": True, "session": {"id": request.session_id}, "db_error": str(e)}
    
    return {"success": True, "session": {"id": request.session_id}, "db_available": False}


@app.post("/session/end")
async def end_session(request: SessionEnd):
    """
    End a game session and update leaderboard.
    
    Stores final stats in Vultr PostgreSQL.
    """
    global db_client
    
    if db_client:
        try:
            result = await db_client.end_session(
                session_id=request.session_id,
                patience_end=request.patience_end,
                deal_closed=request.deal_closed,
                turns=request.turns
            )
            
            # Update leaderboard if user_id provided
            if request.user_id:
                await db_client.update_leaderboard(
                    user_id=request.user_id,
                    username=request.username,
                    won=request.deal_closed or request.patience_end >= 100,
                    turns=request.turns,
                    patience_end=request.patience_end
                )
            
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {"success": True, "db_available": False}


@app.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(limit: int = 10):
    """
    Get the top players leaderboard.
    
    Returns top players by wins from Vultr PostgreSQL.
    """
    global db_client
    
    if db_client:
        try:
            entries = await db_client.get_leaderboard(limit=limit)
            return entries
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Return empty if database not configured
    return []


@app.get("/session/{session_id}")
async def get_session_details(session_id: str):
    """Get session details by ID."""
    global db_client
    
    if db_client:
        try:
            session = await db_client.get_session_by_id(session_id)
            if session:
                return session
            raise HTTPException(status_code=404, detail="Session not found")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    raise HTTPException(status_code=503, detail="Database not configured")
