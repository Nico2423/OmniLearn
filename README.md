# OmniLearn - Adaptive Learning Platform

OmniLearn is an AI-powered adaptive learning platform that creates personalized learning paths for any topic. The application generates knowledge trees, lesson content, and practice questions with feedback to help students learn effectively.

## Features

- **Knowledge Tree Generation**: Create a structured learning path for any topic
- **Personalized Lesson Content**: AI-generated educational content for each topic
- **Adaptive Practice Questions**: Questions that adjust to your knowledge level
- **Real-time Feedback**: Get immediate feedback on your answers
- **Progress Tracking**: Track your learning journey
- **Multimedia Support**: Visual aids to enhance learning (optional)

## Tech Stack

### Frontend
- Next.js
- Tailwind CSS
- Shadcn UI
- TanStack Query
- React Hook Form
- Zod

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- OpenAI API
- Alembic

### Infrastructure
- Docker
- Docker Compose

## Getting Started

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/omnilearn.git
cd omnilearn
```

2. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key
```

3. Start the application using Docker Compose:
```bash
docker compose up -d
```

4. Run database migrations:
```bash
docker compose exec backend alembic upgrade head
```

5. Access the application:
   - Frontend: http://localhost:12000
   - Backend API: http://localhost:12001
   - API Documentation: http://localhost:12001/api/v1/docs
   - Database: localhost:15432 (postgres/postgres)

## Usage

1. Enter a topic you want to learn about
2. Navigate through the generated knowledge tree
3. Read the lesson content for each subsection
4. Practice with questions to test your understanding
5. Get feedback on your answers and track your progress

## Development

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Backend Development

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
