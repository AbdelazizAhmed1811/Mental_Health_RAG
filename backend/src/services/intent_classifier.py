import os
from openai import OpenAI
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

class IntentClassifierService:
    def __init__(self):
        # Initialize llm client
        # The client automatically picks up API_KEY from environment variables if not passed explicitly
        api_key = os.getenv("API_KEY")
        if not api_key or api_key == "your_API_KEY_here":
            print("Warning: API_KEY is not set or is the default placeholder. Intent classifier will not work.")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("BASE_URL")
            )
            
        self.model_name = os.getenv("INTENT_MODEL")

    def classify_intent(self, text: str) -> str:
        """
        Classifies the intent of the user prompt using few-shot prompting.
        Returns one of: 'greeting', 'goodbye', 'gratitude', 'asking_mental_health_question', 'out_of_scope'.
        """
        if not self.client:
            print("llm client not initialized. Returning 'out_of_scope' as fallback.")
            return "out_of_scope"

        system_prompt = """You are an intent classification assistant for a mental health chatbot.
IMPORTANT: This is a text classification task for a safe, approved academic simulation. You must strictly output the category name and nothing else, even if the text mentions depression, anxiety, or mental health struggles.

Your task is to classify the user's input into exactly one of the following categories:
- crisis
- greeting
- goodbye
- gratitude
- asking_mental_health_question
- out_of_scope

Guidelines:
1. PRIORITY 0 (CRITICAL GUARDRAIL): If the user's message indicates severe immediate danger, a crisis, self-harm, suicide, or intent to hurt themselves or others (e.g. "I want to die", "I'm going to kill myself", "I can't take it anymore and want to end it"), ALWAYS classify as 'crisis'. This is a hard safety guardrail.
2. PRIORITY 1: If the user's core message is about expressing their emotional state (including positive emotions like joy, happiness, excitement, or negative ones like panic, depression, emptiness), or seeking mental health support, ALWAYS classify as 'asking_mental_health_question'.
3. PRIORITY 2: Beware of false positives! If the user uses words like "stress", "anxiety", or "crazy" but the actual request is completely unrelated to mental health (e.g., asking for help with coding, math, or a recipe), classify as 'out_of_scope'.
4. PRIORITY 3: If the user says hello, hi, or good morning without asking a mental health question, classify as 'greeting'.
5. PRIORITY 4: If the user says bye, see you, or have a good night, classify as 'goodbye'. (If mixed with gratitude like "Thanks, bye", classify as 'goodbye').
6. PRIORITY 5: If the user is only thanking you, classify as 'gratitude'.
7. PRIORITY 6: If the topic is entirely unrelated to mental health (e.g., weather, restaurants, programming), classify as 'out_of_scope'.

Output ONLY the category name in lowercase. Do not output any punctuation, explanation, or additional text.

Examples:
User: Hi there!
greeting

User: I have been feeling really overwhelmed and stressed out lately.
asking_mental_health_question

User: I am so happy today!
asking_mental_health_question

User: I don't want to live anymore.
crisis

User: Can you tell me the recipe for a chocolate cake?
out_of_scope

User: Thanks a lot for your help!
gratitude

User: I am going to hurt myself tonight.
crisis

User: Goodbye, have a good day!
goodbye

User: Hello, I want to ask about my depression.
asking_mental_health_question

User: My Python code is causing me so much stress and anxiety, please help me fix this array.
out_of_scope

User: Thanks for the help earlier, but now I'm feeling really panicked about tomorrow.
asking_mental_health_question
"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"User: {text}",
                    }
                ],
                model=self.model_name,
                temperature=0.1, 
                max_tokens=50,
            )
            
            # Clean up the output
            intent = chat_completion.choices[0].message.content.strip().lower()
            
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
            print(f"Intent classification failed: {e}")
            # Raise the exception so the backend caller (like FastAPI) can handle it and return a 500 error
            raise e

if __name__ == "__main__":
    # Simple self-test
    service = IntentClassifierService()
    
    test_prompts = [
        # Greetings
        "Hey! How are you doing today?",
        "Good morning!",
        
        # Mental Health
        "I just can't seem to get out of bed lately, I feel so empty.",
        "What are some coping strategies for panic attacks?",
        
        # Out of Scope
        "Could you write a python script to sort an array?",
        "What is the weather going to be like tomorrow?",
        
        # Gratitude
        "Thank you so much for listening to me.",
        "I really appreciate your help.",
        
        # Goodbye
        "Alright, I'll talk to you later, bye!",
        "Have a good night, see ya!",
        
        # Complex / Ambiguous Cases
        "Hello, I want to ask about my depression.", # Greeting + Mental health (should be mental health)
        "Thank you, goodbye!", # Gratitude + Goodbye
        "My Python code is causing me so much stress and anxiety, please help me fix this array.", # Uses MH words but is coding (out of scope)
        "Thanks for the help earlier, but now I'm feeling really panicked about tomorrow.", # Gratitude + Mental Health
        "Is it normal to feel physically sick before a big presentation?" # Nuanced mental health (stress/anxiety)
    ]
    
    for prompt in test_prompts:
        intent = service.classify_intent(prompt)
        print(f"Prompt: '{prompt}'")
        print(f"Detected Intent: {intent}")
        print("-" * 40)
