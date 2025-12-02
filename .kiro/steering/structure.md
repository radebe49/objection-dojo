# Project Structure

```
├── backend/                 # FastAPI backend service
│   ├── main.py             # App entry point, CORS config, routes
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
│
├── frontend/               # Next.js frontend application
│   ├── src/
│   │   └── app/            # App Router pages and layouts
│   │       ├── layout.tsx  # Root layout with fonts
│   │       ├── page.tsx    # Home page
│   │       ├── globals.css # Global styles
│   │       └── fonts/      # Local font files
│   ├── tailwind.config.ts  # Tailwind with custom colors
│   ├── tsconfig.json       # TypeScript config
│   └── package.json        # Node dependencies
│
└── .kiro/                  # Kiro configuration
    ├── steering/           # AI assistant guidance
    └── specs/              # Feature specifications
```

## Architecture
- **Monorepo**: Separate `frontend/` and `backend/` directories
- **Frontend**: Next.js App Router pattern (file-based routing in `src/app/`)
- **Backend**: Single FastAPI application with CORS enabled for frontend

## Conventions
- Frontend components go in `frontend/src/components/` (create as needed)
- API routes defined in `backend/main.py` or separate route modules
- Environment variables: copy `.env.example` to `.env` and configure
- Backend serves API on port 8000, frontend on port 3000
