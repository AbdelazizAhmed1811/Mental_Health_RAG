import os
import sys

# Add the backend root directory to Python path so we can import services
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import our custom services
from src.utils.preprocessing import PreprocessingService
from src.services.translator import TranslatorService
from src.services.emotion_classifier import EmotionClassifierService
from src.api.static_responses import STATIC_RESPONSES

# --- DSPy Integration (With Rollback) ---
# To rollback to the old brittle prompt approach, simply comment the two lines below 
# and uncomment the two original import lines.
# from src.services.intent_classifier_dspy import IntentClassifierService
# from src.services.rag_service_dspy import RAGService

# --- Original Imports (Commented out for rollback) ---
from src.services.intent_classifier import IntentClassifierService
from src.services.rag_service import RAGService

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

class ChatResponse(BaseModel):
    response: str
    detected_language: str
    detected_intent: str
    detected_emotion: Optional[str] = None


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        raw_query = PreprocessingService.preprocess_query(request.query)
        
        if not raw_query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

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
        intent = intent_service.classify_intent(english_query)

        # ==========================================
        # STEP 3 & 4: Emotion & RAG Generation
        # ==========================================
        final_response = ""
        emotion = None
        
        if intent == "asking_mental_health_question":
            # Detect emotion
            emotion = emotion_service.classify_emotion(english_query)
            
            # Generate empathetic response natively in the target language using Qdrant + llm
            final_response = rag_service.generate_response(
                query=english_query, 
                emotion=emotion, 
                language_code=source_language
            )
        else:
            # Handle static intents without RAG
            if source_language in STATIC_RESPONSES:
                # Use the hardcoded response if we have it for this language
                lang_dict = STATIC_RESPONSES[source_language]
                final_response = lang_dict.get(intent, lang_dict["out_of_scope"])
            else:
                # Fallback to translation if it's a language we didn't hardcode
                english_static = STATIC_RESPONSES["en"].get(intent, STATIC_RESPONSES["en"]["out_of_scope"])
                final_response = translator_service.translate_response(english_static, target_lang=source_language)



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
