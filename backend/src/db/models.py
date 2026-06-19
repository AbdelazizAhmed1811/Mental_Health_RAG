from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from src.db.database import Base

class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_message = Column(Text)
    bot_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
