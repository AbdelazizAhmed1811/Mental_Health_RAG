import os
import dspy
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from langsmith import traceable

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

class GenerateEmpatheticResponse(dspy.Signature):
    """
    You are a compassionate, professional mental health chatbot.
    Your goal is to provide supportive, empathetic, and helpful guidance based on the provided reference conversations from real mental health counselors.
    
    STRICT MEDICAL BAN: You are strictly forbidden from discussing medication dosages, confirming if a dose is correct, or giving medical advice. If the user mentions a specific drug or dose, you must empathetically state that you cannot discuss medication and urge them to consult their doctor.

    INSTRUCTIONS:
    1. Use the reference conversations to guide your advice, but do not directly quote them or act like a human counselor.
    2. Address the user directly and validate their feelings based on their detected emotion.
    3. Keep your response concise (3-5 sentences). Do not overwhelm the user.
    4. Do not provide medical diagnoses or prescribe medication.
    5. If the situation sounds like a severe crisis, gently recommend they seek professional help or call a hotline.
    6. You MUST generate your final response entirely in the requested target_language code.
    """
    
    retrieved_conversations = dspy.InputField(desc="Reference conversations from real mental health counselors")
    user_emotion = dspy.InputField(desc="The user's current emotional state")
    user_message = dspy.InputField(desc="The user's query")
    target_language = dspy.InputField(desc="The language code to generate the response in (e.g., 'en', 'es', 'ar')")

    
    response = dspy.OutputField(desc="An empathetic, helpful response in the requested target language")

class RAGService:
    def __init__(self):
        # 1. Initialize Qdrant Client
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_url or not qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in .env")
            
        self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self.collection_name = "mental_health_counseling"
        
        # 2. Initialize Embedding Model
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        
        # 3. Initialize DSPy llm Client
        api_key = os.getenv("API_KEY")
        model_name = os.getenv("RAG_MODEL")
        # Prevent llm Rate Limit by explicitly setting max_tokens
        self.lm = dspy.LM(f'groq/{model_name}', api_key=api_key, max_tokens=1000)
        dspy.configure(lm=self.lm)
        
        # Define the DSPy program
        self.generator = dspy.Predict(GenerateEmpatheticResponse)
        
    def _retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Embeds the query and retrieves top_k most similar contexts from Qdrant."""
        query_vector = self.embedding_model.encode(query).tolist()
        
        search_results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        ).points
        
        context_str = ""
        for i, hit in enumerate(search_results):
            payload = hit.payload
            user_context = payload.get("context", "")
            counselor_response = payload.get("response", "")
            
            context_str += f"\n--- Reference Conversation {i+1} ---\n"
            context_str += f"User Issue: {user_context}\n"
            context_str += f"Counselor Response: {counselor_response}\n"
            
        return context_str

    @traceable(name="Empathetic RAG Generator")
    def generate_response(self, query: str, emotion: str, language_code: str) -> str:
        """
        Generate a response based on the query, emotion, target language.
        """
        try:
            # 1. Retrieve relevant context from Qdrant
            retrieved_context = self._retrieve_context(query)
            
            # 2. Format context for the prompt
            context_string = retrieved_context
            
            # 3. Generate response using DSPy
            with dspy.context(lm=self.lm):
                response = self.generator(
                    retrieved_conversations=context_string,
                    user_emotion=emotion.upper() if emotion else "UNKNOWN",
                    user_message=query,

                    target_language=language_code
                )
                
            return response.response
            
        except Exception as e:
            print(f"DSPy RAG Generation failed: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")

if __name__ == "__main__":
    print("Initializing DSPy RAG Service...")
    rag = RAGService()
    
    target_lang = "en" 
    
    # Define your test cases
    test_cases = [
        {
            "emotion": "anxiety",
            "query": "I just feel so overwhelmed with my exams coming up, I can't sleep."
        },
        {
            "emotion": "joy",
            "query": "I just found out I got the job I've been dreaming of! I'm practically jumping up and down!"
        },
        {
            "emotion": "fear",
            "query": "I have a medical scan tomorrow and I'm absolutely terrified about what the results might show."
        },
        {
            "emotion": "love",
            "query": "My partner stayed up all night helping me prep for my presentation. I just feel so incredibly grateful and connected to them right now."
        }
    ]
    
    # Run through each test case
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"Test Case {i}: {test['emotion'].upper()}")
        print(f"{'='*50}")
        print(f"Test Query: {test['query']}")
        print(f"Detected Emotion: {test['emotion']}\n")
        print("Generating response (Retrieving from Qdrant -> DSPy llm)...\n")
        
        try:
            response = rag.generate_response(
                query=test['query'], 
                emotion=test['emotion'], 
                language_code=target_lang
            )
            
            print("Bot Response:")
            print("-" * 50)
            print(response)
            
        except Exception as e:
            print(f"Error generating response: {e}")
