# Tech Stack

## Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS with custom "Corporate Clean" color scheme
- **Animation**: Framer Motion
- **Icons**: Lucide React
- **Fonts**: Geist Sans/Mono (local), Inter (extended)

## Backend
- **Framework**: FastAPI
- **Language**: Python 3
- **Validation**: Pydantic v2
- **HTTP Client**: httpx
- **Server**: Uvicorn

## External Services
- Cerebras API (AI/LLM)
- ElevenLabs API (text-to-speech)
- LiquidMetal Raindrop SmartMemory

## Common Commands

### Frontend (from `frontend/` directory)
```bash
npm run dev      # Start dev server (localhost:3000)
npm run build    # Production build
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Backend (from `backend/` directory)
```bash
pip install -r requirements.txt    # Install dependencies
uvicorn main:app --reload          # Start dev server (localhost:8000)
```

## Code Style
- Frontend: ESLint with Next.js core-web-vitals and TypeScript rules
- Path aliases: `@/*` maps to `./src/*`
- Use Tailwind utility classes; extend theme in `tailwind.config.ts`
