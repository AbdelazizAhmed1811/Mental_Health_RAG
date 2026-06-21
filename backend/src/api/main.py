import os
import sys

# Add the backend root directory to Python path so we can import services
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

# Import our custom services
from src.utils.preprocessing import PreprocessingService
from src.services.translator import TranslatorService
from src.services.emotion_classifier import EmotionClassifierService
from src.api.static_responses import STATIC_RESPONSES

# --- DSPy Integration (With Rollback) ---
from src.services.intent_classifier_dspy import IntentClassifierService
from src.services.rag_service_dspy import RAGService

from src.db.database import SessionLocal, init_db
from src.db import crud
from src.api import auth

# Initialize DB
init_db()

app = FastAPI(
    title="Mental Health RAG Chatbot API",
    description="A complete pipeline integrating translation, intent routing, emotion detection, and Qdrant RAG.",
)

# --- CORS Setup ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(auth.router)

# --- Service Initialization ---
# We initialize these globally so they are loaded once when the server starts
try:
    print("Initializing services...")
    translator_service = TranslatorService()
    intent_service = IntentClassifierService()
    emotion_service = EmotionClassifierService()
    rag_service = RAGService()
    print("All services initialized successfully!")
except Exception as e:
    print(f"ERROR: Failed to initialize services. Make sure Qdrant, llm, and Models are configured. Details: {e}")

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    detected_language: str
    detected_intent: str
    detected_emotion: Optional[str] = None


@app.get("/health")
def health_check():
    return {"status": "healthy"}

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

# Optional Auth dependency for chat
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", auto_error=False)
def get_optional_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(auth.get_db)):
    if token:
        try:
            return auth.get_current_user(token, db)
        except HTTPException:
            pass
    return None

@app.get("/api/sessions", tags=["sessions"])
def get_sessions(current_user = Depends(auth.get_current_user), db = Depends(auth.get_db)):
    return crud.get_user_sessions(db, current_user.id)

@app.get("/api/sessions/{session_id}", tags=["sessions"])
def get_session(session_id: str, current_user = Depends(auth.get_current_user), db = Depends(auth.get_db)):
    return crud.get_session_messages(db, session_id, current_user.id)

@app.delete("/api/sessions/{session_id}", tags=["sessions"])
def delete_session(session_id: str, current_user = Depends(auth.get_current_user), db = Depends(auth.get_db)):
    crud.delete_session(db, session_id, current_user.id)
    return {"status": "deleted"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, current_user = Depends(get_optional_user), db = Depends(auth.get_db)):
    try:
        raw_query = PreprocessingService.preprocess_query(request.query)
        
        if not raw_query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        # Fetch recent history
        history_str = crud.get_recent_history(db, request.session_id) if request.session_id else ""

        # ==========================================
        # STEP 1: Language Detection & Translation
        # ==========================================
        processed = translator_service.process_prompt(raw_query)
        source_language = processed["language"]
        english_query = processed["english_text"]

        # ==========================================
        # STEP 2: Intent Classification
        # ==========================================
        # We classify intent based on the English query for better LLM accuracy
        intent_result = intent_service.classify_intent(english_query, history=history_str)
        
        # Handle both string (original) and tuple (DSPy ChainOfThought) return types
        if isinstance(intent_result, tuple):
            intent = intent_result[0]
        else:
            intent = intent_result

        # ==========================================
        # STEP 3 & 4: Emotion & RAG Generation
        # ==========================================
        final_response = ""
        emotion = None
        
        bot_english = ""
        if intent == "asking_mental_health_question":
            # Detect emotion
            emotion = emotion_service.classify_emotion(english_query, history=history_str)
            
            # Generate empathetic response natively in English using Qdrant + LLM
            bot_english = rag_service.generate_response(
                query=english_query, 
                emotion=emotion, 
                history=history_str
            )
            # Translate to user's native language
            final_response = translator_service.translate_response(bot_english, target_lang=source_language)
        else:
            # Handle static intents without RAG
            bot_english = STATIC_RESPONSES["en"].get(intent, STATIC_RESPONSES["en"]["out_of_scope"])
            if source_language in STATIC_RESPONSES:
                # Use the hardcoded response if we have it for this language
                lang_dict = STATIC_RESPONSES[source_language]
                final_response = lang_dict.get(intent, lang_dict["out_of_scope"])
            else:
                # Fallback to translation if it's a language we didn't hardcode
                final_response = translator_service.translate_response(bot_english, target_lang=source_language)

        # Save to history
        if request.session_id:
            user_id = current_user.id if current_user else None
            crud.add_conversation_turn(db, request.session_id, english_query, bot_english, user_id, emotion)

        # Return the comprehensive payload
        return ChatResponse(
            response=final_response,
            detected_language=source_language,
            detected_intent=intent,
            detected_emotion=emotion
        )

    except HTTPException:
        raise
    except Exception as e:
        # If any internal service fails, bubble up a 500
        print(f"Chat Endpoint Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

        
# --- Serve Frontend Static Files ---
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist")

@app.middleware("http")
async def add_frontend_fallback(request, call_next):
    # This middleware allows React Router to handle its own client-side routes.
    # If the path doesn't start with /api or /chat, and isn't a static asset file,
    # we serve index.html
    response = await call_next(request)
    if response.status_code == 404 and not request.url.path.startswith("/api"):
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return response

if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
