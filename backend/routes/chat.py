"""Chat routes with streaming support."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json

from backend.database.connection import get_db
from backend.database.models import ChatHistory, Course
from backend.models.schemas import ChatMessage, ChatResponse
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(message: ChatMessage, db: Session = Depends(get_db)):
    """Stream a chat response."""
    # Validate course
    course = db.query(Course).filter(Course.id == message.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Save user message
    user_msg = ChatHistory(
        course_id=message.course_id,
        role="user",
        content=message.content,
        mode=message.mode
    )
    db.add(user_msg)
    db.commit()

    # Get chat history for context
    history = db.query(ChatHistory).filter(
        ChatHistory.course_id == message.course_id
    ).order_by(ChatHistory.created_at.desc()).limit(20).all()

    chat_history = [
        {"role": h.role, "content": h.content}
        for h in reversed(history)
    ]

    async def generate():
        full_response = ""
        async for chunk in orchestrator.teach(
            course_id=message.course_id,
            query=message.content,
            mode=message.mode,
            chat_history=chat_history
        ):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"

        # Save assistant response
        assistant_msg = ChatHistory(
            course_id=message.course_id,
            role="assistant",
            content=full_response,
            mode=message.mode
        )
        db.add(assistant_msg)
        db.commit()

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("")
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    """Non-streaming chat endpoint."""
    from backend.services.ai_provider import chat_completion
    from backend.agents.prompts import TEACHING_AGENT_PROMPT
    from backend.rag.vector_store import vector_store

    # Validate course
    course = db.query(Course).filter(Course.id == message.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Save user message
    user_msg = ChatHistory(
        course_id=message.course_id,
        role="user",
        content=message.content,
        mode=message.mode
    )
    db.add(user_msg)
    db.commit()

    # Get context
    context_docs = vector_store.search(message.course_id, message.content, n_results=5)
    context = "\n\n".join([d["text"] for d in context_docs]) if context_docs else ""

    # Get history
    history = db.query(ChatHistory).filter(
        ChatHistory.course_id == message.course_id
    ).order_by(ChatHistory.created_at.desc()).limit(10).all()

    messages = [
        {"role": "system", "content": TEACHING_AGENT_PROMPT}
    ]
    if context:
        messages.append({"role": "system", "content": f"STUDENT'S NOTES:\n{context}"})

    for h in reversed(history[1:]):  # Exclude the message we just saved
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": message.content})

    # Generate response
    response = chat_completion(messages, temperature=0.3)

    # Save response
    assistant_msg = ChatHistory(
        course_id=message.course_id,
        role="assistant",
        content=response,
        mode=message.mode
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(
        id=assistant_msg.id,
        role="assistant",
        content=response,
        mode=message.mode,
        metadata={},
        created_at=assistant_msg.created_at
    )


@router.get("/history/{course_id}", response_model=List[ChatResponse])
def get_chat_history(course_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Get chat history for a course."""
    messages = db.query(ChatHistory).filter(
        ChatHistory.course_id == course_id
    ).order_by(ChatHistory.created_at.desc()).limit(limit).all()

    return [
        ChatResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            mode=m.mode,
            metadata=m.extra_metadata or {},
            created_at=m.created_at
        )
        for m in reversed(messages)
    ]


@router.delete("/history/{course_id}")
def clear_chat_history(course_id: int, db: Session = Depends(get_db)):
    """Clear chat history for a course."""
    db.query(ChatHistory).filter(ChatHistory.course_id == course_id).delete()
    db.commit()
    return {"message": "Chat history cleared"}
