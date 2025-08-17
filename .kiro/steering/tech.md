# Technology Stack

## Frontend
- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS 4.0 with Shadcn UI components
- **State Management**: TanStack Query for server state
- **Forms**: React Hook Form with Zod validation
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Markdown**: React Markdown for content rendering

## Backend
- **Framework**: FastAPI with Python 3.9+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **AI Integration**: Multiple LLM providers (OpenAI, OpenRouter, Gemini, Ollama)
- **Authentication**: Python-JOSE for JWT tokens
- **Validation**: Pydantic v2 for data validation
- **Testing**: Pytest with async support

## Infrastructure
- **Containerization**: Docker with Docker Compose
- **Database**: PostgreSQL 15
- **Ports**: Frontend (12000), Backend (12001), Database (15432)

## Build System
- **Frontend**: npm with Next.js build system
- **Backend**: UV package manager with Hatchling build backend
- **Code Quality**: Black formatter, isort for imports

## Common Commands

### Development Setup
```bash
# Full stack with Docker
docker-compose up -d

# Frontend development
cd frontend && npm install && npm run dev

# Backend development  
cd backend && uv pip install -e . && uvicorn app.main:app --reload

# Database migrations
cd backend && alembic upgrade head
```

### Environment Variables
- `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY`: AI provider keys
- `AI_PROVIDER`: Provider selection (openai, openrouter, gemini)
- `AI_MODEL`: Model specification
- `ENABLE_MULTIMEDIA`: Feature flag for multimedia generation
- `POSTGRES_*`: Database connection settings
- `SECRET_KEY`: JWT token signing key
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: Google OAuth credentials