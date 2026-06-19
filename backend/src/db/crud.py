from sqlalchemy.orm import Session
from src.db.models import ConversationHistory

def add_conversation_turn(db: Session, session_id: str, user_msg: str, bot_msg: str):
    """Adds a single conversation turn to the database."""
    if not session_id:
        return None
    db_turn = ConversationHistory(
        session_id=session_id,
        user_message=user_msg,
        bot_message=bot_msg
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
