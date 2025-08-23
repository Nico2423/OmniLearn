from fastapi import APIRouter

from app.api.endpoints import knowledge_tree, lessons, questions, users, auth, organizations, courses

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(knowledge_tree.router, prefix="/knowledge-tree", tags=["knowledge-tree"])
api_router.include_router(lessons.router, tags=["lessons"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
