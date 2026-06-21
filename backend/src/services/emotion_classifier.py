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
            
        self.session_ema = {}
        self.alpha = 0.5  # EMA smoothing factor
        
        self.emotion_labels = ["LABEL_0", "LABEL_1", "LABEL_2", "LABEL_3", "LABEL_4", "LABEL_5"]
        self.emotion_mapping = {
            "LABEL_0": "sadness",
            "LABEL_1": "joy",
            "LABEL_2": "love",
            "LABEL_3": "anger",
            "LABEL_4": "fear",
            "LABEL_5": "surprise"
        }
        self.idx_to_emotion = {i: self.emotion_mapping[label] for i, label in enumerate(self.emotion_labels)}
        self.label_to_idx = {label: i for i, label in enumerate(self.emotion_labels)}

    def classify_emotion(self, text: str, session_id: str = None) -> str:
        """
        Calls the external emotion classifier running on Colab via Ngrok.
        Uses EMA to smooth emotions over the session.
        If the URL is not set or fails, gracefully falls back to 'neutral'.
        """
        if not self.url or self.url == "your_ngrok_url_here":
            return "neutral"
            
        try:
            # Pass ONLY the Latest Message to DistilBERT
            response = requests.post(f"{self.url}/predict", json={"text": text}, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            raw_emotion = data.get("emotion", "neutral")
            
            if raw_emotion not in self.label_to_idx:
                return self.emotion_mapping.get(raw_emotion, raw_emotion)
                
            emotion_idx = self.label_to_idx[raw_emotion]
            
            if session_id:
                if session_id not in self.session_ema:
                    self.session_ema[session_id] = [0.0] * len(self.emotion_labels)
                    self.session_ema[session_id][emotion_idx] = 1.0
                else:
                    for i in range(len(self.emotion_labels)):
                        self.session_ema[session_id][i] *= (1 - self.alpha)
                    self.session_ema[session_id][emotion_idx] += self.alpha
                    
                best_idx = max(range(len(self.emotion_labels)), key=self.session_ema[session_id].__getitem__)
                return self.idx_to_emotion[best_idx]
            else:
                return self.emotion_mapping.get(raw_emotion, raw_emotion)
            
        except Exception as e:
            print(f"Emotion classification failed: {e}. Falling back to 'neutral'.")
            if session_id and session_id in self.session_ema:
                ema_state = self.session_ema[session_id]
                best_idx = max(range(len(ema_state)), key=ema_state.__getitem__)
                return self.idx_to_emotion[best_idx]
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
