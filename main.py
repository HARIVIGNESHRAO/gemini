from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
from database import SessionLocal, ChatThread, Message
# Updated import for the new SDK
from google import genai 
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

# Initialize the new Client
client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="AI Chat Backend - Gemini")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    thread_id: Optional[int] = None
    message: str

@app.post("/threads/")
def create_thread(title: str = "New Chat", db=Depends(get_db)):
    thread = ChatThread(title=title)
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread

@app.get("/threads/")
def get_threads(db=Depends(get_db)):
    return db.query(ChatThread).all()

@app.get("/threads/{thread_id}/messages")
def get_messages(thread_id: int, db=Depends(get_db)):
    return db.query(Message).filter(Message.thread_id == thread_id).order_by(Message.id).all()

@app.post("/chat")
def chat(request: ChatRequest, db=Depends(get_db)):
    if not request.thread_id:
        thread = ChatThread(title="New Chat")
        db.add(thread)
        db.commit()
        db.refresh(thread)
        thread_id = thread.id
    else:
        thread = db.query(ChatThread).filter(ChatThread.id == request.thread_id).first()
        if not thread:
            raise HTTPException(404, "Thread not found")
        thread_id = request.thread_id

    # Save user message
    db.add(Message(thread_id=thread_id, role="user", content=request.message))
    db.commit()

    # Get conversation history
    history = db.query(Message).filter(Message.thread_id == thread_id).order_by(Message.id).all()
    
    # Prepare messages for Gemini using the new SDK's Content type
    contents = []
    for msg in history:
        role = "user" if msg.role == "user" else "model"
        contents.append(types.Content(
            role=role,
            parts=[types.Part.from_text(text=msg.content)]
        ))

    # Call Gemini using the updated model identifier
    # Using 'gemini-2.0-flash' as it is the current standard stable release
# Change from gemini-1.5-flash to gemini-2.5-flash
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=contents
    )
    reply = response.text

    # Save assistant reply
    assistant_msg = Message(thread_id=thread_id, role="assistant", content=reply)
    db.add(assistant_msg)
    db.commit()

    # Auto-update thread title after first message
    if len(history) == 1:
        thread.title = request.message[:50] + ("..." if len(request.message) > 50 else "")
        db.commit()

    return {"thread_id": thread_id, "reply": reply}