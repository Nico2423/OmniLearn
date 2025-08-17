# Project Structure

## Root Level
- `.env` - Environment variables for development
- `docker-compose.yml` - Multi-service container orchestration
- `README.md` - Main project documentation
- `LICENSE` - MIT license file

## Backend (`backend/`)
FastAPI application following clean architecture patterns:

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   ├── api.py           # Main API router
│   │   └── endpoints/       # Route handlers by domain
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── organizations.py # Organization management
│   │       ├── courses.py   # Course management
│   │       ├── knowledge_tree.py
│   │       ├── lessons.py
│   │       ├── questions.py
│   │       └── users.py
│   ├── core/
│   │   ├── config.py        # Settings and configuration
│   │   └── security.py      # Authentication utilities
│   ├── db/
│   │   ├── session.py       # Database session management
│   │   └── init_db.py       # Database initialization
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py          # User model with OAuth support
│   │   ├── organization.py  # Organization and invite models
│   │   ├── course.py        # Course and enrollment models
│   │   ├── knowledge_tree.py
│   │   ├── lesson.py
│   │   └── question.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── user.py          # User schemas with OAuth
│   │   ├── organization.py  # Organization schemas
│   │   ├── course.py        # Course and progress schemas
│   │   └── ...
│   └── services/            # Business logic layer
│       ├── auth.py          # Authentication and OAuth
│       ├── organization.py  # Organization management
│       ├── course.py        # Course and enrollment logic
│       └── ...
├── pyproject.toml           # Python project configuration
└── Dockerfile               # Container build instructions
```

## Frontend (`frontend/`)
Next.js application with App Router:

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout component
│   ├── page.tsx             # Home page
│   ├── globals.css          # Global styles
│   ├── components/          # React components
│   │   ├── ui/              # Shadcn UI components
│   │   └── [feature].tsx    # Feature-specific components
│   └── lib/
│       ├── api.ts           # API client utilities
│       └── utils.ts         # Utility functions
├── components/              # Legacy component location (duplicate)
├── lib/                     # Legacy lib location (duplicate)
├── package.json             # Node.js dependencies
└── Dockerfile               # Container build instructions
```

## Documentation (`docs/`)
- `backend-rules.md` - Backend development guidelines
- `frontend-rules.md` - Frontend development guidelines

## Planning (`plans/`)
- `PRD.md` - Product Requirements Document

## Architecture Patterns

### Backend
- **Layered Architecture**: API → Services → Models → Database
- **Domain-Driven Design**: Organized by business domains (knowledge_tree, lessons, questions, users)
- **Dependency Injection**: Settings and database sessions injected via FastAPI
- **Schema Separation**: Pydantic schemas separate from SQLAlchemy models

### Frontend
- **Component-Based**: Reusable UI components with Shadcn
- **Server State Management**: TanStack Query for API data
- **Form Handling**: React Hook Form with Zod validation
- **API Layer**: Centralized API client in `lib/api.ts`

### File Naming Conventions
- **Backend**: Snake_case for Python files and functions
- **Frontend**: PascalCase for components, camelCase for utilities
- **Database**: Snake_case for table and column names