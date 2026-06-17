import os
from openai import OpenAI
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Resolve path to the backend/.env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

class RAGService:
    def __init__(self):
        # 1. Initialize Qdrant Client
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_url or not qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in .env")
            
        self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self.collection_name = "mental_health_counseling"
        
        # 2. Initialize Embedding Model (Must match the one used in Colab)
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        # CPU is fine here since it's just encoding one query at a time
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        
        # 3. Initialize OpenAI Client (pointing to llm)
        self.llm_client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("BASE_URL")
        )
        self.llm_model = os.getenv("INTENT_MODEL")
        
    def _retrieve_context(self, query: str, top_k: int = 1) -> str:
        """Embeds the query and retrieves top_k most similar contexts from Qdrant."""
        # Embed the user's query
        query_vector = self.embedding_model.encode(query).tolist()
        
        # Search Qdrant
        search_results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        ).points
        
        # Format the retrieved results into a readable string for the LLM
        context_str = ""
        for i, hit in enumerate(search_results):
            # We stored 'context' (user problem) and 'response' (counselor reply) in the payload
            payload = hit.payload
            user_context = str(payload.get("context", ""))[:1500]
            counselor_response = str(payload.get("response", ""))[:1500]
            
            context_str += f"\n--- Reference Conversation {i+1} ---\n"
            context_str += f"User Issue: {user_context}\n"
            context_str += f"Counselor Response: {counselor_response}\n"
            
        return context_str

    def generate_response(self, query: str, emotion: str, language_code: str = "en") -> str:
        """
        Generates an empathetic response using llm, grounded in retrieved Qdrant context,
        tailored to the user's detected emotion, and returned natively in the requested language.
        """
        # 1. Retrieve relevant conversations
        retrieved_context = self._retrieve_context(query)
        
        # 2. Construct the prompt
        system_prompt = f"""You are a compassionate, professional mental health chatbot.
Your goal is to provide supportive, empathetic, and helpful guidance based on the provided reference conversations from real mental health counselors.

CURRENT USER EMOTION: The user's current emotional state has been detected as: {emotion.upper()}
You MUST tailor your tone to be highly sensitive to this emotion. If they are angry, be calming. If they are sad, be deeply empathetic and warm.

LANGUAGE REQUIREMENT: You MUST generate your final response entirely in the language corresponding to the ISO-639-1 language code: '{language_code}'. Do not include English unless the code is 'en'.


RETRIEVED CONVERSATIONS FOR REFERENCE:
{retrieved_context}

INSTRUCTIONS:
1. Use the reference conversations to guide your advice, but do not directly quote them or act like a human counselor.
2. Address the user directly and validate their feelings based on their detected emotion.
3. Keep your response concise (3-5 sentences). Do not overwhelm the user.
4. Do not provide medical diagnoses or prescribe medication.
5. If the situation sounds like a severe crisis, gently recommend they seek professional help or call a hotline.
"""

        try:
            # 3. Call llm
            chat_completion = self.llm_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                model=self.llm_model,
                temperature=0.6,
                max_tokens=256
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"RAG Generation failed: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")

if __name__ == "__main__":
    # Simple self-test
    print("Initializing RAG Service...")
    rag = RAGService()
    
    test_query = "I just feel so overwhelmed with my exams coming up, I can't sleep."
    test_emotion = "anxiety"
    
    print(f"\\nTest Query: {test_query}")
    print(f"Detected Emotion: {test_emotion}\\n")
    print("Generating response (Retrieving from Qdrant -> llm)...\\n")
    
    response = rag.generate_response(query=test_query, emotion=test_emotion)
    print("Bot Response:")
    print("-" * 50)
    print(response)
    print("-" * 50)
