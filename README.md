# Dealfu

AI-powered sales simulation training application that helps users practice handling customer objections through realistic voice-enabled conversations.

## Overview

Dealfu is a real-time sales simulation where users practice their pitch against "The Skeptic CTO" - an AI persona that evaluates pitches and responds with realistic objections. The app features:

- **Voice-enabled interactions** using Web Speech API for speech-to-text
- **AI-generated responses** via Cerebras API
- **Text-to-speech playback** via ElevenLabs API
- **Dynamic Patience Meter** showing pitch performance (0-100%)
- **Win/Loss conditions** based on convincing the AI or losing patience

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                        │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────┐               │
│  │  Lobby   │→ │  Simulation  │→ │  Win/Loss   │               │
│  │  Screen  │  │    Screen    │  │   Screen    │               │
│  └──────────┘  └──────────────┘  └─────────────┘               │
│                       │                                         │
│              Web Speech API (STT)                               │
└───────────────────────┼─────────────────────────────────────────┘
                        │ POST /chat
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Orchestrator Service                     │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │  │  Cerebras   │  │  ElevenLabs │  │   SmartMemory   │   │  │
│  │  │   Client    │  │    Client   │  │     Client      │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Validation**: Pydantic v2
- **HTTP Client**: httpx

### External Services
- **Cerebras API** - AI/LLM for conversation
- **ElevenLabs API** - Text-to-speech
- **LiquidMetal Raindrop** - Session memory storage

## Local Development Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- npm or yarn

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

Frontend runs at http://localhost:3000

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and add your API keys
cp .env.example .env

# Start development server
uvicorn main:app --reload
```

Backend runs at http://localhost:8000

## Environment Variables

### Frontend (`frontend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

### Backend (`backend/.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `CEREBRAS_API_KEY` | Cerebras API key for AI responses | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for TTS | Yes |
| `ELEVENLABS_VOICE_ID` | Voice ID for TTS | Yes |
| `RAINDROP_API_KEY` | LiquidMetal Raindrop API key | Yes |
| `PRODUCTION_DOMAIN` | Frontend domain for CORS | Production only |

## Deployment

### Frontend (Vercel)

1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` = Your backend URL
3. Deploy

### Backend (Docker/Vultr)

```bash
cd backend

# Build Docker image
docker build -t dealfu-api .

# Run container
docker run -d \
  --name dealfu-api \
  -p 8000:8000 \
  --env-file .env.production \
  dealfu-api
```

Or use docker-compose:

```bash
docker-compose up -d
```

## API Endpoints

### `POST /chat`

Process user message and return AI response with audio.

**Request:**
```json
{
  "session_id": "uuid-string",
  "user_text": "Your sales pitch here",
  "current_patience": 50
}
```

**Response:**
```json
{
  "ai_text": "AI response text",
  "patience_score": 65,
  "deal_closed": false,
  "audio_base64": "base64-encoded-mp3"
}
```

### `GET /health`

Health check endpoint.

## Testing

### Frontend Tests
```bash
cd frontend
npm run test        # Run tests
npm run test:watch  # Watch mode
```

### Backend Tests
```bash
cd backend
pytest              # Run all tests
pytest -v           # Verbose output
```

## License

MIT
