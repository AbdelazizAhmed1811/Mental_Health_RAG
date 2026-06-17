import os
import joblib
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()

class TranslatorService:
    def __init__(self):
        # Load the language classification model
        model_path = os.getenv("LANG_MODEL_PATH")
        try:
            self.lang_model = joblib.load(model_path)
        except Exception as e:
            print(f"Warning: Could not load language model at {model_path}: {e}")
            self.lang_model = None

    def detect_language(self, text: str) -> str:
        """Detect the language of the text using the pre-trained model."""
        if self.lang_model:
            # The model pipeline handles text preprocessing and prediction
            prediction = self.lang_model.predict([text])
            return prediction[0]
        else:
            return "unknown"

    def process_prompt(self, text: str) -> dict:
        """
        Takes a prompt, detects its language, and translates to English if necessary.
        Returns a dictionary with the original text, detected language, and English text.
        """
        lang = self.detect_language(text)
        
        # If language is English ('en') or unknown, skip translation
        if lang == 'en' or lang == 'unknown':
            english_text = text
        else:
            try:
                # Use deep_translator to translate to English
                # GoogleTranslator auto-detects the exact source dialect, which is robust
                translator = GoogleTranslator(source='auto', target='en')
                english_text = translator.translate(text)
            except Exception as e:
                print(f"Translation failed: {e}")
                # Fallback to original text if translation fails
                english_text = text
                
        return {
            "original_text": text,
            "language": lang,
            "english_text": english_text
        }

    def translate_response(self, text: str, target_lang: str) -> str:
        """
        Translate the generated English response back to the user's target language.
        """
        if target_lang == 'en' or target_lang == 'unknown':
            return text
            
        try:
            # Note: GoogleTranslator supports many languages, but the target code must be a valid ISO-639-1 code.
            # Assuming the language model outputs standard ISO codes (e.g. 'sw', 'bg', 'de').
            translator = GoogleTranslator(source='en', target=target_lang)
            translated_text = translator.translate(text)
            return translated_text
        except Exception as e:
            print(f"Response translation failed: {e}")
            return text

if __name__ == "__main__":
    # Simple self-test
    service = TranslatorService()
    
    test_prompts = [
        "I am feeling very anxious today.",  # English
        "Me siento muy triste y deprimido.",  # Spanish
        "انا اشعر بالتوتر والقلق",            # Arabic
        "Ich habe Angst vor der Zukunft."     # German
    ]
    
    for prompt in test_prompts:
        result = service.process_prompt(prompt)
        print(f"Original: {result['original_text']}")
        print(f"Detected Lang: {result['language']}")
        print(f"English: {result['english_text']}")
        print("-" * 40)
