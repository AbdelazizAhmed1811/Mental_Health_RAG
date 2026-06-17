import os
import requests
from dotenv import load_dotenv

def test_emotion_api():
    # Load environment variables
    load_dotenv()
    
    # Get the URL
    url = os.getenv("EMOTION_CLASSIFIER_URL")
    if not url or url == "your_ngrok_url_here":
        print("❌ Error: EMOTION_CLASSIFIER_URL is not set correctly in your .env file.")
        print("Please set it to your Ngrok public URL (e.g., https://<id>.ngrok-free.app)")
        return
    
    # The predict endpoint
    predict_url = f"{url.rstrip('/')}/predict"
    print(f"Testing Emotion Classifier API at: {predict_url}")
    print("-" * 50)
    
    # Test cases covering different potential emotions and tricky edge-cases
    test_cases = [
        # Standard clear emotions
        "I feel so completely hopeless, I can't stop crying.",
        "I am so incredibly angry right now, I want to break something!",
        "I'm terrified about my exam tomorrow, my heart is racing.",
        "I just got promoted at work and I'm feeling wonderful!",
    ]
    
    success_count = 0
    for i, text in enumerate(test_cases, 1):
        print(f"Test {i}: '{text}'")
        try:
            response = requests.post(predict_url, json={"text": text}, timeout=15)
            
            # Check if Ngrok is showing a warning page (status 200 but HTML content)
            if "text/html" in response.headers.get("Content-Type", ""):
                print("❌ Failed: Ngrok returned an HTML page. You might need to visit the URL in your browser first to accept the Ngrok warning, or the Colab server isn't running properly.")
                continue
                
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Result: {data.get('emotion', 'UNKNOWN')} (Score: {data.get('score', 'N/A')})")
            success_count += 1
            
        except requests.exceptions.Timeout:
            print("❌ Failed: Request timed out. Is the Colab notebook still running?")
        except requests.exceptions.ConnectionError:
            print("❌ Failed: Connection error. Is the Ngrok URL correct and online?")
        except requests.exceptions.HTTPError as e:
            print(f"❌ Failed: HTTP Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"❌ Failed: Unexpected error: {e}")
        
        print("-" * 50)
        
    print(f"\nTest Summary: {success_count}/{len(test_cases)} passed.")

if __name__ == "__main__":
    test_emotion_api()
