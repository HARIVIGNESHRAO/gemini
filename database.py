from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatThread(Base):
    __tablename__ = "threads"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("threads.id"))
    role = Column(String(50))  # "user" or "assistant"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    thread = relationship("ChatThread", back_populates="messages")

# Create tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("✅ Database initialized!")