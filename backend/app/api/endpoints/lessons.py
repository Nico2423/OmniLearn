from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Any, List
import json
import asyncio
import time
import logging

from app.db.session import get_async_session
from app.schemas.lesson import LessonCreate, LessonResponse
from app.services.lesson import LessonService
from app.models.lesson import Lesson, ReasoningTrace
from app.services.ai import AIService
from app.services.trace_persistence import save_trace, append_markdown

router = APIRouter(prefix="/lessons", tags=["lessons"])
logger = logging.getLogger(__name__)

# Load system prompt
try:
    with open("app/prompts/lesson_stream_prompt.txt", "r") as f:
        SYSTEM_PROMPT = f.read().strip()
except FileNotFoundError:
    SYSTEM_PROMPT = "You are an expert tutor AI."

@router.post("/", response_model=LessonResponse)
async def create_lesson(
    data: LessonCreate,
    service: LessonService = Depends(),
) -> Any:
    """
    Generate lesson content for a subsection.
    """
    try:
        return await service.generate_lesson(data.subsection_id, data.subsection_title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream")
async def stream_lesson_get(
    subsection_id: int,
    subsection_title: str,
    db: AsyncSession = Depends(get_async_session),
    ai: AIService = Depends()
):
    """
    Stream newline-delimited reasoning traces + Markdown lesson via GET request.
    Buffers tokens until a newline; saves JSON traces to DB.
    """
    # Check if lesson already exists, create if not
    stmt = select(Lesson).where(Lesson.subsection_id == subsection_id)
    result = await db.execute(stmt)
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        # Try to create a new lesson, handle race conditions
        lesson = Lesson(
            subsection_id=subsection_id,
            content=""  # Will be updated as we receive content
        )
        try:
            db.add(lesson)
            await db.commit()
            await db.refresh(lesson)
        except IntegrityError:
            # Another request created the lesson simultaneously, fetch the existing one
            await db.rollback()
            logger.warning(f"Race condition detected for lesson with subsection_id {subsection_id}. Fetching existing lesson.")
            result = await db.execute(stmt)
            lesson = result.scalar_one_or_none()
            if not lesson:
                # If still no lesson, something went wrong
                raise HTTPException(status_code=500, detail="Failed to retrieve or create lesson")
    

    def token_text(t):
        return t if isinstance(t, str) else (t.choices[0].delta.content or "")

    async def event_generator():
        system_prompt = open("app/prompts/lesson_stream_prompt.txt").read().strip()
        buffer = ""
        last_sent = time.monotonic()
        
        try:
            ai_stream = ai.stream_completion([
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": f"<LESSON_REQUEST>{subsection_title}</LESSON_REQUEST>"}
            ])

            async for token in ai_stream:
                # Heartbeat every 25 seconds
                if time.monotonic() - last_sent > 25:
                    yield {"comment": "ping"}
                    last_sent = time.monotonic()
                
                if not token:  # ignore empty keep-alives
                    continue
                    
                text = token_text(token)
                buffer += text

                # flush each complete line
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        # Detect JSON vs Markdown
                        is_json = line.lstrip().startswith("{") and line.rstrip().endswith("}")
                        
                        if is_json:
                            try:
                                obj = json.loads(line)
                                if obj.get("step_type"):  # it's a trace
                                    await save_trace(db, lesson.id, obj)
                                elif obj.get("event"):  # forward model's own events
                                    # Handle events that may not have a "data" key
                                    if "data" in obj:
                                        yield {"event": obj["event"], "data": obj["data"]}
                                    else:
                                        yield {"event": obj["event"]}
                                else:  # regular JSON data
                                    yield {"data": line}
                            except json.JSONDecodeError:
                                yield {"data": line}
                        else:
                            await append_markdown(db, lesson, line + "\n")
                            yield {"data": line}

            # send any residue after stream ends
            if buffer.strip():
                is_json = buffer.lstrip().startswith("{") and buffer.rstrip().endswith("}")
                if is_json:
                    try:
                        obj = json.loads(buffer)
                        if obj.get("step_type"):  # it's a trace
                            await save_trace(db, lesson.id, obj)
                        elif obj.get("event"):  # forward model's own events
                            # Handle events that may not have a "data" key
                            if "data" in obj:
                                yield {"event": obj["event"], "data": obj["data"]}
                            else:
                                yield {"event": obj["event"]}
                        else:  # regular JSON data
                            yield {"data": buffer}
                    except json.JSONDecodeError:
                        yield {"data": buffer}
                else:
                    await append_markdown(db, lesson, buffer + "\n")
                    yield {"data": buffer}

            # Final commit for any remaining data
            await db.commit()
            
        except Exception as exc:
            logger.exception("stream_lesson failed")
            await db.rollback()
            yield {"event": "error", "data": json.dumps({"error": str(exc)})}
            # Keep the SSE connection alive
            try:
                while True:
                    await asyncio.sleep(30)
                    yield {"comment": "keepalive"}
            except asyncio.CancelledError:
                pass

    return EventSourceResponse(event_generator(), headers={
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    })

@router.post("/stream")
async def stream_lesson(data: LessonCreate, db: AsyncSession = Depends(get_async_session), ai: AIService = Depends()):
    """
    Stream newline-delimited reasoning traces + Markdown lesson.
    Buffers tokens until a newline; saves JSON traces to DB.
    """
    # Check if lesson already exists, create if not
    stmt = select(Lesson).where(Lesson.subsection_id == data.subsection_id)
    result = await db.execute(stmt)
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        # Try to create a new lesson, handle race conditions
        lesson = Lesson(
            subsection_id=data.subsection_id,
            content=""  # Will be updated as we receive content
        )
        try:
            db.add(lesson)
            await db.commit()
            await db.refresh(lesson)
        except IntegrityError:
            # Another request created the lesson simultaneously, fetch the existing one
            await db.rollback()
            logger.warning(f"Race condition detected for lesson with subsection_id {data.subsection_id}. Fetching existing lesson.")
            result = await db.execute(stmt)
            lesson = result.scalar_one_or_none()
            if not lesson:
                # If still no lesson, something went wrong
                raise HTTPException(status_code=500, detail="Failed to retrieve or create lesson")
    

    def token_text(t):
        return t if isinstance(t, str) else (t.choices[0].delta.content or "")

    async def event_generator():
        system_prompt = open("app/prompts/lesson_stream_prompt.txt").read().strip()
        buffer = ""
        last_sent = time.monotonic()
        
        try:
            ai_stream = ai.stream_completion([
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": f"<LESSON_REQUEST>{data.subsection_title}</LESSON_REQUEST>"}
            ])

            async for token in ai_stream:
                # Heartbeat every 25 seconds
                if time.monotonic() - last_sent > 25:
                    yield {"comment": "ping"}
                    last_sent = time.monotonic()
                
                if not token:  # ignore empty keep-alives
                    continue
                    
                text = token_text(token)
                buffer += text

                # flush each complete line
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        # Detect JSON vs Markdown
                        is_json = line.lstrip().startswith("{") and line.rstrip().endswith("}")
                        
                        if is_json:
                            try:
                                obj = json.loads(line)
                                if obj.get("step_type"):  # it's a trace
                                    await save_trace(db, lesson.id, obj)
                                elif obj.get("event"):  # forward model's own events
                                    # Handle events that may not have a "data" key
                                    if "data" in obj:
                                        yield {"event": obj["event"], "data": obj["data"]}
                                    else:
                                        yield {"event": obj["event"]}
                                else:  # regular JSON data
                                    yield {"data": line}
                            except json.JSONDecodeError:
                                yield {"data": line}
                        else:
                            await append_markdown(db, lesson, line + "\n")
                            yield {"data": line}

            # send any residue after stream ends
            if buffer.strip():
                is_json = buffer.lstrip().startswith("{") and buffer.rstrip().endswith("}")
                if is_json:
                    try:
                        obj = json.loads(buffer)
                        if obj.get("step_type"):  # it's a trace
                            await save_trace(db, lesson.id, obj)
                        elif obj.get("event"):  # forward model's own events
                            # Handle events that may not have a "data" key
                            if "data" in obj:
                                yield {"event": obj["event"], "data": obj["data"]}
                            else:
                                yield {"event": obj["event"]}
                        else:  # regular JSON data
                            yield {"data": buffer}
                    except json.JSONDecodeError:
                        yield {"data": buffer}
                else:
                    await append_markdown(db, lesson, buffer + "\n")
                    yield {"data": buffer}

            # Final commit for any remaining data
            await db.commit()
            
        except Exception as exc:
            logger.exception("stream_lesson failed")
            await db.rollback()
            yield {"event": "error", "data": json.dumps({"error": str(exc)})}
            # Keep the SSE connection alive
            try:
                while True:
                    await asyncio.sleep(30)
                    yield {"comment": "keepalive"}
            except asyncio.CancelledError:
                pass

    return EventSourceResponse(event_generator(), headers={
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    })

@router.get("/subsection/{subsection_id}", response_model=LessonResponse)
async def get_lesson_by_subsection(
    subsection_id: int,
    service: LessonService = Depends(),
) -> Any:
    """
    Get a lesson by subsection ID. Auto-generates if it doesn't exist.
    """
    lesson = await service.get_lesson_by_subsection(subsection_id)
    if not lesson:
        # Auto-generate lesson if it doesn't exist
        try:
            from app.models.knowledge_tree import Subsection
            
            # This should be updated to use async session as well
            from app.db.session import get_db
            db = next(get_db())
            subsection = db.query(Subsection).filter(Subsection.id == subsection_id).first()
            if not subsection:
                raise HTTPException(status_code=404, detail="Subsection not found")
            
            lesson = await service.generate_lesson(subsection_id, subsection.title)
            return lesson
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate lesson: {str(e)}")
    return lesson

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: int,
    service: LessonService = Depends(),
) -> Any:
    """
    Get a lesson by ID.
    """
    lesson = await service.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
