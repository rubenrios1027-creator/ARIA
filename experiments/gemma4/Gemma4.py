import requests
import json

# Docker Model Runner endpoint (requires TCP enabled)
DMR_URL = "http://localhost:12434/engines/v1/chat/completions"

# Run: docker model ls  — to confirm your exact model name
MODEL = "gemma4:e2b"  # adjust to match your pulled model tag

def chat():
    print(f"=== Gemma 4 Chat (Docker Model Runner) ===")
    print("Type 'exit' or 'quit' to end the session.\n")

    conversation_history = []

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            print("Ending session.")
            break

        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        payload = {
            "model": MODEL,
            "messages": conversation_history
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(DMR_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # OpenAI-style response — different from Ollama's format
            assistant_reply = data["choices"][0]["message"]["content"]

            conversation_history.append({
                "role": "assistant",
                "content": assistant_reply
            })

            print(f"\nGemma: {assistant_reply}\n")

        except requests.exceptions.ConnectionError:
            print("ERROR: Cannot reach Docker Model Runner.")
            print("Make sure TCP is enabled: docker desktop enable model-runner --tcp 12434")
            break
        except Exception as e:
            print(f"ERROR: {e}")
            break

if __name__ == "__main__":
    chat()