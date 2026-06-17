import os
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

class EmotionClassifierService:
    def __init__(self):
        self.url = os.getenv("EMOTION_CLASSIFIER_URL")
        if not self.url:
            print("WARNING: EMOTION_CLASSIFIER_URL is not set in .env. Will default to 'neutral'.")

    def classify_emotion(self, text: str) -> str:
        """
        Calls the external emotion classifier running on Colab via Ngrok.
        If the URL is not set or fails, gracefully falls back to 'neutral'.
        """
        if not self.url or self.url == "your_ngrok_url_here":
            return "neutral"
            
        try:
            response = requests.post(f"{self.url}/predict", json={"text": text}, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            raw_emotion = data.get("emotion", "neutral")
            
            emotion_mapping = {
                "LABEL_0": "sadness",
                "LABEL_1": "joy",
                "LABEL_2": "love",
                "LABEL_3": "anger",
                "LABEL_4": "fear",
                "LABEL_5": "surprise"
            }
            
            return emotion_mapping.get(raw_emotion, raw_emotion)
            
        except Exception as e:
            print(f"Emotion classification failed: {e}. Falling back to 'neutral'.")
            return "neutral"

if __name__ == "__main__":
    
    service = EmotionClassifierService()
    
    cases = [
        "I am feeling so hopeless and sad today.",
        "I just got the best news ever, I am so thrilled!",
        "I am absolutely terrified of the storm outside."
    ]
    
    for text in cases:
        emotion = service.classify_emotion(text)
        print(f"Text: '{text}'")
        print(f"Detected Emotion: {emotion}")
        print("-" * 30)
