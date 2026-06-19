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
        self.retrieval_mode = os.getenv("RETRIEVAL_MODE", "dense").lower()
        
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
        
        # 2. Initialize Embedding Model (Must match the one used in Colab)
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        # CPU is fine here since it's just encoding one query at a time
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        
        # 3. Initialize OpenAI Client (pointing to llm)
        self.llm_client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("BASE_URL")
        )
        self.llm_model = os.getenv("RAG_MODEL")
        
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
        retrieved_context = self._retrieve_context(query,3)
        # print(retrieved_context)
        # 2. Construct the prompt
        system_prompt = f"""You are a compassionate, professional mental health chatbot.
Your goal is to provide supportive, empathetic, and helpful guidance based on the provided reference conversations from real mental health counselors.

CURRENT USER EMOTION: The user's current emotional state has been detected as: {emotion.upper()}
You MUST tailor your tone to be highly sensitive to this emotion. If they are angry, be calming. If they are sad, be deeply empathetic and warm.

LANGUAGE REQUIREMENT: You MUST generate your final response entirely in the language corresponding to the ISO-639-1 language code: '{language_code}'. Do not include English unless the code is 'en'.


RETRIEVED CONVERSATIONS FOR REFERENCE:
the following is a conversation between a patient and a mental health counselor. Use these as context to inform your response, but do not quote them directly or act like a human counselor. Instead, provide advice in your own words.
{retrieved_context}

INSTRUCTIONS:
1. Use the reference conversations to guide your advice, but do not directly quote them or act like a human counselor.
2. Address the user directly and validate their feelings based on their detected emotion.
3. If the situation sounds like a severe crisis, gently recommend they seek professional help or call a hotline.
3. Keep your response concise (5-7 sentences). Do not overwhelm the user.
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
                max_tokens=1024
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"RAG Generation failed: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")

if __name__ == "__main__":
    # Simple self-test
    print("Initializing RAG Service...")
    rag = RAGService()
    
    test_query = "I have fear of commitment and it is affecting my relationships. I feel like I am always running away from something. What should I do?"
    test_emotion = "anxiety"
    
    print(f"\\nTest Query: {test_query}")
    print(f"Detected Emotion: {test_emotion}\\n")
    print("Generating response (Retrieving from Qdrant -> llm)...\\n")
    
    response = rag.generate_response(query=test_query, emotion=test_emotion)
    print("Bot Response:")
    print("-" * 50)
    print(response)
    print("-" * 50)
