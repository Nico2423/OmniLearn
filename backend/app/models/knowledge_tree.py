from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class KnowledgeTree(Base, TimestampMixin):
    __tablename__ = "knowledge_trees"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)

    sections = relationship("Section", back_populates="tree", cascade="all, delete-orphan")
    course = relationship("Course", back_populates="knowledge_tree", uselist=False)


class Section(Base, TimestampMixin):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    tree_id = Column(Integer, ForeignKey("knowledge_trees.id"))
    title = Column(String, index=True)
    description = Column(Text)

    tree = relationship("KnowledgeTree", back_populates="sections")
    subsections = relationship("Subsection", back_populates="section", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="section", cascade="all, delete-orphan")


class Subsection(Base, TimestampMixin):
    __tablename__ = "subsections"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    title = Column(String, index=True)
    description = Column(Text)

    section = relationship("Section", back_populates="subsections")
    lesson = relationship("Lesson", back_populates="subsection", uselist=False, cascade="all, delete-orphan")