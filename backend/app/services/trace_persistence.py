from sqlalchemy.ext.asyncio import AsyncSession
from app.models.lesson import ReasoningTrace, Lesson
import json
import asyncio

# In-memory counters for commit batching
trace_counter = 0
markdown_counter = 0

async def save_trace(db: AsyncSession, lesson_id: int, trace_dict: dict):
    """Save a reasoning trace to the database, committing every 5 writes."""
    global trace_counter
    
    trace = ReasoningTrace(
        lesson_id=lesson_id,
        step_number=trace_dict["step_number"],
        step_type=trace_dict["step_type"],
        content=trace_dict["content"]
    )
    db.add(trace)
    
    trace_counter += 1
    if trace_counter >= 5:
        await db.commit()
        trace_counter = 0

async def append_markdown(db: AsyncSession, lesson: Lesson, line: str):
    """Append markdown content to a lesson, committing every 5 writes."""
    global markdown_counter
    
    if lesson.content:
        lesson.content += line
    else:
        lesson.content = line
    
    markdown_counter += 1
    if markdown_counter >= 5:
        await db.commit()
        markdown_counter = 0
