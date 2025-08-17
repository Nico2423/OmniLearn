# Technology Stack

## Frontend
- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS 4.0 with Shadcn UI components
- **State Management**: TanStack Query for server state
- **Forms**: React Hook Form with Zod validation
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Markdown**: React Markdown for content rendering

### ⚠️ Important: Tailwind CSS v4 + Shadcn Compatibility

**Issue**: Shadcn UI components were designed for Tailwind CSS v3, but this project uses Tailwind CSS v4. This causes CSS variable mapping issues where Shadcn buttons appear unstyled.

**Solution**: The `frontend/app/globals.css` file contains special CSS variable mappings to make Shadcn components work with Tailwind v4:

```css
:root {
  --background: #ffffff;
  --foreground: #0f172a;
  --primary: #1e40af;
  --primary-foreground: #ffffff;
  /* ... other variables */
}

@theme {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  /* ... mappings for all Shadcn variables */
}
```

**Key Points**:
- DO NOT remove the `@theme` block in globals.css
- CSS variables must be named without the `--color-` prefix in `:root`
- The `@theme` block maps them to the `--color-*` format that Shadcn expects
- If Shadcn components appear unstyled, check that all required CSS variables are mapped

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