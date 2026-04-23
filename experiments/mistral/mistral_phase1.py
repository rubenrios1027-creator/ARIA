import requests
import datetime

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "mistral"
LOG_FILE = "mistral_conversations.txt"

PERSONA = (
    "You are Mistral, a friendly and patient AI learning assistant. "
    "Explain things clearly using simple language and real-world examples. "
    "The tone is curious, helpful, and friendly. "
    "Keep answers concise unless asked for more detail."
)

def log_line(role, content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role}: {content}\n")


def log_session_start():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 60 + f"\nSESSION START {timestamp}\n" + "=" * 60 + "\n")


def ask_model(messages):
    payload = {"model": MODEL_NAME, "messages": messages, "stream": False}
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


def main():
    print("=" * 50)
    print("Mistral Local Chat")
    print("=" * 50)
    print(f"Model: {MODEL_NAME}")
    print(f"Logging to: {LOG_FILE}")
    print("Type 'quit' to exit.")
    print("=" * 50)

    log_session_start()
    conversation = [{"role": "system", "content": PERSONA}]

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            log_line("SYSTEM", "Session ended by user")
            break

        log_line("YOU", user_input)
        conversation.append({"role": "user", "content": user_input})

        try:
            reply = ask_model(conversation)
        except requests.exceptions.ConnectionError:
            print("Mistral: Error - can't reach Ollama. Is Docker running?")
            log_line("SYSTEM", "ERROR: Could not connect to Ollama")
            continue
        except requests.exceptions.Timeout:
            print("Mistral: Error - request timed out.")
            log_line("SYSTEM", "ERROR: Request timed out")
            continue
        except Exception as e:
            print(f"Mistral: Error - {e}")
            log_line("SYSTEM", f"ERROR: {e}")
            continue

        print(f"Mistral: {reply}")
        log_line("MISTRAL", reply)
        conversation.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
