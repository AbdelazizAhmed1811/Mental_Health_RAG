from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from src.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    display_name = Column(String)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_id = Column(Integer, index=True, nullable=True) # Optional for anonymous users
    user_message = Column(Text)
    bot_message = Column(Text)
    emotion = Column(String, nullable=True) # To store the detected emotion for the preview
    timestamp = Column(DateTime, default=datetime.utcnow)
