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
        self.retrieval_mode = os.getenv("RETRIEVAL_MODE", "hybrid").lower()
        
        # Register text payload index on 'context' field for keyword/hybrid matching
        try:
            from qdrant_client.http import models
            self.qdrant_client.create_payload_index(
                collection_name=self.collection_name,
                field_name="context",
                field_schema=models.TextIndexParams(
                    type=models.TextIndexType.TEXT,
                    tokenizer=models.TokenizerType.WORD,
                    lowercase=True,
                    max_token_len=15,
                    min_token_len=2
                )
            )
            print("Payload text index on 'context' registered successfully or already exists.")
        except Exception as e:
            print(f"Warning: Could not create payload text index: {e}")
        
        # 2. Initialize Embedding Model
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        
        # 3. Initialize DSPy llm Client
        api_key = os.getenv("API_KEY")
        model_name = os.getenv("INTENT_MODEL")
        # Prevent llm Rate Limit by explicitly setting max_tokens
        self.lm = dspy.LM(f'groq/{model_name}', api_key=api_key, max_tokens=15000)
        dspy.configure(lm=self.lm)
        
        # Define the DSPy program
        self.generator = dspy.Predict(GenerateEmpatheticResponse)
        
    def _retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieves top_k most similar contexts from Qdrant using the configured retrieval mode.
        Supports: 'dense', 'keyword', and 'hybrid'.
        """
        from qdrant_client.http import models

        results = []

        if self.retrieval_mode == "dense":
            # Pure Dense Vector Similarity Search
            query_vector = self.embedding_model.encode(query).tolist()
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k
            ).points

        elif self.retrieval_mode == "keyword":
            # Pure Keyword / Full-text Search
            results = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="context",
                            match=models.MatchText(text=query)
                        )
                    ]
                ),
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )[0]

        elif self.retrieval_mode == "hybrid":
            # Hybrid Search via Reciprocal Rank Fusion (RRF) on Dense and Keyword results
            # 1. Fetch dense candidates
            query_vector = self.embedding_model.encode(query).tolist()
            dense_results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=20
            ).points

            # 2. Fetch keyword candidates
            keyword_results = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="context",
                            match=models.MatchText(text=query)
                        )
                    ]
                ),
                limit=20,
                with_payload=True,
                with_vectors=False
            )[0]

            # 3. Apply Reciprocal Rank Fusion (RRF)
            # RRF Score = sum( 1 / (k + rank) ) where k is a constant (usually 60)
            rrf_scores = {}
            rrf_constant = 60

            # Rank dense results
            for rank, hit in enumerate(dense_results):
                rrf_scores[hit.id] = {
                    "hit": hit,
                    "score": 1.0 / (rrf_constant + rank + 1)
                }

            # Rank keyword results
            for rank, hit in enumerate(keyword_results):
                if hit.id in rrf_scores:
                    rrf_scores[hit.id]["score"] += 1.0 / (rrf_constant + rank + 1)
                else:
                    rrf_scores[hit.id] = {
                        "hit": hit,
                        "score": 1.0 / (rrf_constant + rank + 1)
                    }

            # Sort by fused score and take top_k
            sorted_rrf = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
            results = [item["hit"] for item in sorted_rrf[:top_k]]

        else:
            # Fallback to dense if unknown mode
            print(f"Warning: Unknown retrieval mode '{self.retrieval_mode}'. Falling back to 'dense'.")
            query_vector = self.embedding_model.encode(query).tolist()
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k
            ).points

        # Format the retrieved results into a readable string for the LLM
        context_str = ""
        for i, hit in enumerate(results):
            payload = hit.payload
            user_context = payload.get("context", "")
            counselor_response = payload.get("response", "")
            
            context_str += f"\n--- Reference Conversation {i+1} ---\n"
            context_str += f"User Issue: {user_context}\n"
            context_str += f"Counselor Response: {counselor_response}\n"
        print(context_str)
        return context_str

    def generate_response(self, query: str, emotion: str, language_code: str = "en") -> str:
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
    test_query = "I am having insomnia, I can't sleep."
    test_emotion = "anxiety"
    print(f"\nTest Query: {test_query}")
    print(f"Detected Emotion: {test_emotion}\n")
    print("Generating response (Retrieving from Qdrant -> DSPy llm)...\n")
    response = rag.generate_response(query=test_query, emotion=test_emotion)
    print("Bot Response:")
    print("-" * 50)
    print(response)
    print("-" * 50)
