from sqlalchemy.orm import Session

from app.models.base import Base
from app.db.session import engine
import app.models.knowledge_tree
import app.models.lesson
import app.models.question
import app.models.user
import app.models.organization
import app.models.course


def init_db() -> None:
    Base.metadata.create_all(bind=engine)