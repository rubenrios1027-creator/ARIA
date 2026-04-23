# Model registry — update this list as your Ollama catalog changes.
# Excludes: nomic-embed-text (embedding only), qwen2.5-coder:1.5b-base (uninstruct),
#           qwen3.5:397b-cloud (no local weights), gemma4:e4b (duplicate hash of gemma4:latest)

MODELS = [
    {"name": "llama3.1:8b",       "family": "llama",   "size_gb": 4.9,  "is_coder": False},
    {"name": "qwen3.5:latest",    "family": "qwen",    "size_gb": 6.6,  "is_coder": False},
    {"name": "hermes3:8b",        "family": "hermes",  "size_gb": 4.7,  "is_coder": False},
    {"name": "qwen2.5-coder:7b",  "family": "qwen",    "size_gb": 4.7,  "is_coder": True},
    {"name": "qwen3-coder:latest","family": "qwen",    "size_gb": 18.0, "is_coder": True},
    {"name": "qwen2.5-coder:14b", "family": "qwen",    "size_gb": 9.0,  "is_coder": True},
    {"name": "gemma4:latest",     "family": "gemma",   "size_gb": 9.6,  "is_coder": False},
    {"name": "mistral:latest",    "family": "mistral", "size_gb": 4.4,  "is_coder": False},
    {"name": "smollm2:latest",    "family": "smollm",  "size_gb": 1.8,  "is_coder": False},
]

# The judge model scores other models' responses.
# Using mistral as judge: general-purpose, already in your roster, not a coder model.
JUDGE_MODEL = "mistral:latest"

OLLAMA_URL    = "http://localhost:11434/api/chat"
MAX_ATTEMPTS  = 3           # per prompt per model before skipping
MAX_CONSEC_FAIL = 3         # consecutive failures before skipping the whole model
REQUEST_TIMEOUT = 180       # seconds — large models (18GB) need headroom
JUDGE_TIMEOUT   = 60        # judge calls are shorter prompts
