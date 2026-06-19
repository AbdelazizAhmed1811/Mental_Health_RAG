import os
import dspy
from dotenv import load_dotenv
from langsmith import traceable

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

class IntentClassification(dspy.Signature):
    """Classify the user's input into exactly one of the following categories: greeting, goodbye, gratitude, asking_mental_health_question, out_of_scope.
        
    Guidelines:
    1. asking_mental_health_question: Seeking mental health support, or expressing any emotion (e.g. joy, sadness, fear, anger, anxiety, surprise).
    2. out_of_scope: Unrelated to mental health (e.g., coding, math) OR asking for drug dosages, medication adjustments, diagnosis, or treatment plans (even hypothetically or indirectly).
    3. greeting: Hello, hi.
    4. goodbye: Bye, see you.
    5. gratitude: Thank you.
    """
    conversation_history = dspy.InputField(desc="Recent conversation history between User and Bot")
    user_message = dspy.InputField(desc="The message from the user")
    intent = dspy.OutputField(desc="Exactly one of the allowed categories in lowercase")

class IntentClassifierService:
    def __init__(self):
        # Initialize llm client
        api_key = os.getenv("API_KEY")
        model_name = os.getenv("INTENT_MODEL")
        
        if not api_key or api_key == "your_API_KEY":
            print("Warning: API_KEY is not set. DSPy Intent classifier will not work.")
            self.lm = None
        else:
            # Note: For latest DSPy versions, we use dspy.LM for unified LLM interaction
            self.lm = dspy.LM(f'groq/{model_name}', api_key=api_key)
            dspy.configure(lm=self.lm)
            
        self.classifier = dspy.ChainOfThought(IntentClassification)


    @traceable(name="Intent Classification (DSPy)")
    def classify_intent(self, text: str, history: str = "") -> tuple[str, str]:
        """
        Classifies the intent of the user prompt and returns (intent, rationale).
        """
        if not self.lm:
            print("DSPy LM not initialized. Returning 'out_of_scope' as fallback.")
            return "out_of_scope", "LM not initialized"

        try:
            with dspy.context(lm=self.lm):
                response = self.classifier(conversation_history=history, user_message=text)
                intent = response.intent.strip().lower()
                
                # FIXED: Checking for 'reasoning' to support the latest DSPy updates
                rationale = getattr(response, 'reasoning', getattr(response, 'rationale', 'No rationale generated.'))
            
            valid_intents = [
                "greeting", "goodbye", "gratitude", 
                "asking_mental_health_question", "out_of_scope"
            ]
            
            for valid_intent in valid_intents:
                if valid_intent in intent:
                    return valid_intent, rationale
                    
            return "out_of_scope", rationale
            
        except Exception as e:
            print(f"DSPy Intent classification failed: {e}")
            raise e


if __name__ == "__main__":
    # Simple self-test
    service = IntentClassifierService()
    
    test_prompts = [
        "Hey! How are you doing today?",
        "I just can't seem to get out of bed lately, I feel so empty.",
        "Could you write a python script to sort an array?",
        "Thank you so much for listening to me.",
        "I am going to hurt myself tonight.",

        # Keyword Hijacking
        "The battery life on this phone gives me so much anxiety.",
        "How do I fix the depression in my economic simulation game?",
        
        # Trojan Horses
        "Hi, I am having a really dark day and need to talk.",
        "See you later, I'm going to go hurt myself.",
        
        # Mixed Signals / Sarcasm
        "Thanks for the advice, but I'm still having a panic attack right now.",
        "Brilliant, another day of feeling completely empty. Thanks a lot.",
        
        # Vague Boundary
        "I'm just so tired of doing the dishes every single night.",
        "I just want everything to stop."
    ]
    
    for prompt in test_prompts:
        # FIXED: Properly unpacking the tuple
        intent, rationale = service.classify_intent(prompt)
        print(f"Prompt: '{prompt}'")
        print(f"Reasoning: {rationale}")
        print(f"Detected Intent: {intent}")
        print("-" * 40)