"""
Vultr PostgreSQL database client for Dealfu.

Stores user sessions, leaderboard, and analytics.
This is a REQUIRED integration for the AI Champion Ship hackathon.

Requirements: Hackathon compliance - Vultr service integration
"""

import os
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Check if database dependencies are available
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy.orm import declarative_base
    from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, select, update
    import asyncpg
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


# Get connection string from environment
DATABASE_URL = os.getenv("VULTR_DATABASE_URL")

# SQLAlchemy setup (only if dependencies available)
if DATABASE_AVAILABLE and DATABASE_URL:
    import ssl
    # Create SSL context for Vultr managed database
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        connect_args={"ssl": ssl_context}
    )
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    Base = declarative_base()
else:
    engine = None
    AsyncSessionLocal = None
    Base = None


class DatabaseClientError(Exception):
    """Base exception for database client errors."""
    pass


# Define models only if SQLAlchemy is available
if DATABASE_AVAILABLE:
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    
    class SessionModel(Base):
        """Game session model - tracks each simulation run."""
        __tablename__ = "sessions"
        
        id = Column(String(36), primary_key=True)
        user_id = Column(String(36), nullable=True)  # Optional until auth added
        patience_start = Column(Integer, default=50)
        patience_end = Column(Integer, nullable=True)
        deal_closed = Column(Boolean, default=False)
        outcome = Column(String(20), nullable=True)  # 'won', 'lost', 'abandoned'
        turns = Column(Integer, default=0)
        created_at = Column(DateTime, default=datetime.utcnow)
        ended_at = Column(DateTime, nullable=True)


    class LeaderboardModel(Base):
        """Leaderboard model - tracks player stats."""
        __tablename__ = "leaderboard"
        
        user_id = Column(String(36), primary_key=True)
        username = Column(String(100), nullable=True)
        wins = Column(Integer, default=0)
        losses = Column(Integer, default=0)
        total_sessions = Column(Integer, default=0)
        best_turns_to_win = Column(Integer, nullable=True)
        avg_patience_end = Column(Integer, default=50)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseClient:
    """
    Async database client for Vultr PostgreSQL.
    
    Provides session tracking and leaderboard functionality
    for the AI Champion Ship hackathon Vultr integration requirement.
    """
    
    def __init__(self):
        """Initialize the database client."""
        if not DATABASE_AVAILABLE:
            raise DatabaseClientError(
                "Database dependencies not installed. "
                "Run: pip install asyncpg sqlalchemy[asyncio]"
            )
        if not DATABASE_URL:
            raise DatabaseClientError(
                "VULTR_DATABASE_URL not configured. "
                "Set it in your .env file."
            )
    
    async def init_db(self) -> None:
        """Create tables if they don't exist."""
        if engine is None:
            raise DatabaseClientError("Database engine not initialized")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Vultr PostgreSQL tables initialized")
    
    @asynccontextmanager
    async def _get_db(self):
        """Get an async database session."""
        if AsyncSessionLocal is None:
            raise DatabaseClientError("Database not configured")
        
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def create_session(
        self, 
        session_id: str, 
        user_id: Optional[str] = None,
        patience_start: int = 50
    ) -> dict:
        """
        Create a new game session.
        
        Args:
            session_id: UUID for the session
            user_id: Optional user ID (for authenticated users)
            patience_start: Starting patience value
        
        Returns:
            Created session data
        """
        async with self._get_db() as db:
            session = SessionModel(
                id=session_id,
                user_id=user_id,
                patience_start=patience_start,
                created_at=datetime.utcnow()
            )
            db.add(session)
            await db.flush()
            return {
                "id": session.id,
                "user_id": session.user_id,
                "patience_start": session.patience_start,
                "created_at": session.created_at.isoformat()
            }
    
    async def update_session_turn(self, session_id: str) -> None:
        """Increment the turn counter for a session."""
        async with self._get_db() as db:
            await db.execute(
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(turns=SessionModel.turns + 1)
            )
    
    async def end_session(
        self, 
        session_id: str, 
        patience_end: int, 
        deal_closed: bool,
        turns: int
    ) -> dict:
        """
        End a game session and update stats.
        
        Args:
            session_id: Session to end
            patience_end: Final patience value
            deal_closed: Whether deal was closed
            turns: Total turns taken
        
        Returns:
            Updated session data
        """
        outcome = "won" if deal_closed or patience_end >= 100 else "lost"
        
        async with self._get_db() as db:
            await db.execute(
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(
                    patience_end=patience_end,
                    deal_closed=deal_closed,
                    outcome=outcome,
                    turns=turns,
                    ended_at=datetime.utcnow()
                )
            )
            return {
                "session_id": session_id,
                "outcome": outcome,
                "patience_end": patience_end,
                "turns": turns
            }
    
    async def get_session_by_id(self, session_id: str) -> Optional[dict]:
        """Get session by ID."""
        async with self._get_db() as db:
            result = await db.execute(
                select(SessionModel).where(SessionModel.id == session_id)
            )
            session = result.scalar_one_or_none()
            if session:
                return {
                    "id": session.id,
                    "user_id": session.user_id,
                    "patience_start": session.patience_start,
                    "patience_end": session.patience_end,
                    "deal_closed": session.deal_closed,
                    "outcome": session.outcome,
                    "turns": session.turns,
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                    "ended_at": session.ended_at.isoformat() if session.ended_at else None
                }
            return None
    
    async def get_leaderboard(self, limit: int = 10) -> list[dict]:
        """
        Get top players by wins.
        
        Args:
            limit: Max number of entries to return
        
        Returns:
            List of leaderboard entries
        """
        async with self._get_db() as db:
            result = await db.execute(
                select(LeaderboardModel)
                .order_by(LeaderboardModel.wins.desc())
                .limit(limit)
            )
            entries = result.scalars().all()
            return [
                {
                    "user_id": e.user_id,
                    "username": e.username,
                    "wins": e.wins,
                    "losses": e.losses,
                    "total_sessions": e.total_sessions,
                    "best_turns_to_win": e.best_turns_to_win,
                    "avg_patience_end": e.avg_patience_end
                }
                for e in entries
            ]
    
    async def update_leaderboard(
        self,
        user_id: str,
        username: Optional[str],
        won: bool,
        turns: int,
        patience_end: int
    ) -> None:
        """
        Update leaderboard entry for a user.
        
        Args:
            user_id: User ID
            username: Display name
            won: Whether they won
            turns: Turns taken
            patience_end: Final patience
        """
        async with self._get_db() as db:
            # Check if entry exists
            result = await db.execute(
                select(LeaderboardModel).where(LeaderboardModel.user_id == user_id)
            )
            entry = result.scalar_one_or_none()
            
            if entry:
                # Update existing
                new_wins = entry.wins + (1 if won else 0)
                new_losses = entry.losses + (0 if won else 1)
                new_total = entry.total_sessions + 1
                new_best = min(entry.best_turns_to_win or 999, turns) if won else entry.best_turns_to_win
                new_avg = ((entry.avg_patience_end * entry.total_sessions) + patience_end) // new_total
                
                await db.execute(
                    update(LeaderboardModel)
                    .where(LeaderboardModel.user_id == user_id)
                    .values(
                        username=username or entry.username,
                        wins=new_wins,
                        losses=new_losses,
                        total_sessions=new_total,
                        best_turns_to_win=new_best,
                        avg_patience_end=new_avg,
                        updated_at=datetime.utcnow()
                    )
                )
            else:
                # Create new entry
                new_entry = LeaderboardModel(
                    user_id=user_id,
                    username=username,
                    wins=1 if won else 0,
                    losses=0 if won else 1,
                    total_sessions=1,
                    best_turns_to_win=turns if won else None,
                    avg_patience_end=patience_end
                )
                db.add(new_entry)


# Singleton instance - only created if configured
_db_client: Optional[DatabaseClient] = None


def get_database_client() -> Optional[DatabaseClient]:
    """
    Get the database client singleton.
    
    Returns None if database is not configured (graceful fallback).
    """
    global _db_client
    
    if not DATABASE_AVAILABLE or not DATABASE_URL:
        return None
    
    if _db_client is None:
        try:
            _db_client = DatabaseClient()
        except DatabaseClientError:
            return None
    
    return _db_client


async def init_database() -> bool:
    """
    Initialize the database (create tables).
    
    Returns True if successful, False if not configured.
    """
    client = get_database_client()
    if client:
        await client.init_db()
        return True
    return False
