from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost:11434")
OLLAMA_URL = f"http://{OLLAMA_HOST}/api/chat"
MODELS_URL = f"http://{OLLAMA_HOST}/api/tags"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/models")
def get_models():
    try:
        resp = requests.get(MODELS_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        models = [{"name": m["name"]} for m in data.get("models", [])]
        return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    model = data.get("model", "smollm2")
    messages = data.get("messages", [])

    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        result = resp.json()
        return jsonify({"message": result.get("message", {})})
    except requests.exceptions.Timeout:
        return jsonify({"error": "Model timed out. Try a smaller model."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
