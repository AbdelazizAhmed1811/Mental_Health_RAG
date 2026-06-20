from sqlalchemy.orm import Session
from src.db.models import ConversationHistory, User
from sqlalchemy import func

def get_or_create_user(db: Session, google_id: str, email: str, display_name: str, avatar_url: str):
    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = User(
            google_id=google_id,
            email=email,
            display_name=display_name,
            avatar_url=avatar_url
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def add_conversation_turn(db: Session, session_id: str, user_msg: str, bot_msg: str, user_id: int = None, emotion: str = None):
    """Adds a single conversation turn to the database."""
    if not session_id:
        return None
    db_turn = ConversationHistory(
        session_id=session_id,
        user_id=user_id,
        user_message=user_msg,
        bot_message=bot_msg,
        emotion=emotion
    )
    db.add(db_turn)
    db.commit()
    db.refresh(db_turn)
    return db_turn

def get_recent_history(db: Session, session_id: str, limit: int = 3) -> str:
    """Fetches the last N turns for a session and returns a formatted string."""
    if not session_id:
        return ""
    
    recent_turns = db.query(ConversationHistory)\
                     .filter(ConversationHistory.session_id == session_id)\
                     .order_by(ConversationHistory.timestamp.desc())\
                     .limit(limit)\
                     .all()
    
    if not recent_turns:
        return ""
    
    # The query returns them in descending order (newest first). 
    # We want to format them chronologically (oldest first).
    recent_turns.reverse()
    
    history_lines = []
    for turn in recent_turns:
        history_lines.append(f"User: {turn.user_message}")
        history_lines.append(f"Bot: {turn.bot_message}")
        
    return "\n".join(history_lines)

def get_user_sessions(db: Session, user_id: int):
    """Returns a list of distinct sessions for a user, with the first message as a preview."""
    
    # Get all turns for the user, ordered by timestamp
    turns = db.query(ConversationHistory)\
              .filter(ConversationHistory.user_id == user_id)\
              .order_by(ConversationHistory.timestamp.asc())\
              .all()
              
    # Extract unique sessions and use the first turn as preview
    sessions_dict = {}
    for turn in turns:
        if turn.session_id not in sessions_dict:
            sessions_dict[turn.session_id] = {
                "session_id": turn.session_id,
                "preview": turn.user_message[:50] + "..." if len(turn.user_message) > 50 else turn.user_message,
                "emotion": turn.emotion,
                "timestamp": turn.timestamp
            }
            
    # Return as list, newest first
    session_list = list(sessions_dict.values())
    session_list.sort(key=lambda x: x["timestamp"], reverse=True)
    return session_list

def get_session_messages(db: Session, session_id: str, user_id: int):
    """Returns all messages for a specific session (verifying ownership)."""
    return db.query(ConversationHistory)\
             .filter(ConversationHistory.session_id == session_id, ConversationHistory.user_id == user_id)\
             .order_by(ConversationHistory.timestamp.asc())\
             .all()

def delete_session(db: Session, session_id: str, user_id: int):
    """Deletes a session if it belongs to the user."""
    db.query(ConversationHistory)\
      .filter(ConversationHistory.session_id == session_id, ConversationHistory.user_id == user_id)\
      .delete()
    db.commit()
