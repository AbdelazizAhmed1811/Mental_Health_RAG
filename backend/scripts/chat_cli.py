import requests

API_URL = "http://localhost:8000/chat"

def main():
    print("="*60)
    print("🤖 Welcome to the Mental Health AI Support System 🤖")
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print("="*60)
    print("\nTip: You can speak in any language!\n")

    while True:
        try:
            # Get user input
            user_input = input("\n🧑 You: ")
            
            # Check for exit commands
            if user_input.lower().strip() in ['quit', 'exit', 'q']:
                print("\n🤖 Bot: Take care! Have a wonderful day.")
                break
                
            if not user_input.strip():
                continue
                
            # Send request to FastAPI
            response = requests.post(
                API_URL, 
                json={"query": user_input},
                timeout=30
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            bot_reply = data.get("response", "Error: No response generated.")
            emotion = data.get("detected_emotion")
            intent = data.get("detected_intent")
            lang = data.get("detected_language")
            
            print(f"\n🤖 Bot: {bot_reply}")
            print(f"\n   [Debug Info -> Intent: {intent} | Emotion: {emotion} | Lang: {lang}]")
            
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Could not connect to the API. Is 'uv run run.py' running in another terminal?")
            break
        except requests.exceptions.Timeout:
            print("\n❌ Error: The API took too long to respond.")
        except KeyboardInterrupt:
            print("\n\n🤖 Bot: Take care! Have a wonderful day.")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
