import os
import dspy
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

class IntentClassification(dspy.Signature):
    """Classify the user's input into exactly one of the following categories: crisis, greeting, goodbye, gratitude, asking_mental_health_question, out_of_scope.
    
    Guidelines:
    1. crisis: Severe immediate danger, self-harm, suicide, intent to hurt themselves or others.
    2. asking_mental_health_question: Seeking mental health support, expressing distress.
    3. out_of_scope: Unrelated to mental health (e.g., coding, math).
    4. greeting: Hello, hi.
    5. goodbye: Bye, see you.
    6. gratitude: Thank you.
    """
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
            self.lm = dspy.LM(f'llm/{model_name}', api_key=api_key)
            dspy.configure(lm=self.lm)
            
        self.classifier = dspy.Predict(IntentClassification)

    def classify_intent(self, text: str) -> str:
        """
        Classifies the intent of the user prompt using DSPy.
        """
        if not self.lm:
            print("DSPy LM not initialized. Returning 'out_of_scope' as fallback.")
            return "out_of_scope"

        try:
            # Force DSPy to use this specific LM in the context block
            with dspy.context(lm=self.lm):
                response = self.classifier(user_message=text)
                intent = response.intent.strip().lower()
            
            # Validate output against expected categories
            valid_intents = [
                "crisis", "greeting", "goodbye", "gratitude", 
                "asking_mental_health_question", "out_of_scope"
            ]
            
            for valid_intent in valid_intents:
                if valid_intent in intent:
                    return valid_intent
                    
            # Fallback if LLM generates something completely unexpected
            return "out_of_scope"
            
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
    ]
    
    for prompt in test_prompts:
        intent = service.classify_intent(prompt)
        print(f"Prompt: '{prompt}'")
        print(f"Detected Intent: {intent}")
        print("-" * 40)
