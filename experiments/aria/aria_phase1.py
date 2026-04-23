import requests
import json
import datetime

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4:e4b"
LOG_FILE = "aria_conversations.txt"
ARIA_PERSONA = """You are ARIA, a friendly and patient AI learning assistant.
You explain things clearly using simple language and real-world examples.
You ask one follow-up question after each explanation to check understanding.
Keep your answers concise — 3 to 5 sentences unless asked for more detail."""

def log_message(role, content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {role}: {content}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_line)

def ask_aria(conversation_history):
    payload = {
        "model": MODEL_NAME,
        "messages": conversation_history,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]

def log_session_start():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = f"\n{'='*60}\nNEW SESSION — {timestamp}\n{'='*60}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(separator)

def main():
    print("=" * 50)
    print("  ARIA — Adaptive Readiness & Instruction Assistant")
    print("  Phase 1 | Local AI via SmolLM + Ollama")
    print("=" * 50)
    print(f"  Logging to: {LOG_FILE}")
    print(f"  Model: {MODEL_NAME}")
    print("  Type 'quit' to exit.")
    print("-" * 50)
    log_session_start()
    conversation_history = [
        {"role": "system", "content": ARIA_PERSONA}
    ]
    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("\nARIA: Goodbye! Your conversation has been saved.")
            log_message("System", "Session ended by user.")
            break
        log_message("You", user_input)
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        print("ARIA: ...", end="\r")
        try:
            aria_reply = ask_aria(conversation_history)
        except requests.exceptions.ConnectionError:
            print("ARIA: [Error] Can't reach Ollama. Is Docker running?")
            log_message("System", "ERROR: Could not connect to Ollama.")
            continue
        except requests.exceptions.Timeout:
            print("ARIA: [Error] The model took too long to respond.")
            log_message("System", "ERROR: Request timed out.")
            continue
        except Exception as e:
            print(f"ARIA: [Error] Something unexpected happened: {e}")
            log_message("System", f"ERROR: {e}")
            continue
        print(f"ARIA: {aria_reply}")
        log_message("ARIA", aria_reply)
        conversation_history.append({
            "role": "assistant",
            "content": aria_reply
        })

if __name__ == "__main__":
    main()