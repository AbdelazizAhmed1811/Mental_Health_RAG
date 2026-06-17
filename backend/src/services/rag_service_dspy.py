import os
import dspy
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

class GenerateEmpatheticResponse(dspy.Signature):
    """You are a compassionate, professional mental health chatbot. 
    Your goal is to provide supportive, empathetic, and helpful guidance based on the provided reference conversations from real mental health counselors.
    
    INSTRUCTIONS:
    1. Address the user directly and validate their feelings based on their detected emotion.
    2. Tailor your tone to be highly sensitive to the user's emotion (e.g. calming if angry, deeply empathetic if sad).
    3. Keep your response concise (3-5 sentences). Do not overwhelm the user.
    4. Do not provide medical diagnoses or prescribe medication.
    5. You MUST generate your final response entirely in the requested target_language code.
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
        model_name = os.getenv("INTENT_MODEL")
        # Prevent llm Rate Limit by explicitly setting max_tokens
        self.lm = dspy.LM(f'llm/{model_name}', api_key=api_key, max_tokens=12000)
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
    test_query = "I just feel so overwhelmed with my exams coming up, I can't sleep."
    test_emotion = "anxiety"
    print(f"\nTest Query: {test_query}")
    print(f"Detected Emotion: {test_emotion}\n")
    print("Generating response (Retrieving from Qdrant -> DSPy llm)...\n")
    response = rag.generate_response(query=test_query, emotion=test_emotion)
    print("Bot Response:")
    print("-" * 50)
    print(response)
    print("-" * 50)
