# Project Name / Project Description

This project is a full-stack application, using a web user interface, backend services, and some experimental automation components.

## 📂 Project Structure Overview

The root directory contains the following components:

- **`.claude/`**: Likely configuration or cache files related to AI interactions.
- **`README.md`**: Main documentation file.
- **`index.html`**: The primary front-end entry point.
- **`components/`**: Contains reusable UI elements.
- **`scripts/`**: JavaScript logic files.
- **`data/`**: Data models or configuration files.
- **`config/`**: Application configuration settings.


## Key Components & Functionality

*   **Frontend:** The user interface is handled by HTML, CSS, and JavaScript (loaded via scripts/ and components/).
*   **Backend Logic:** Backend processes are likely managed through specific API endpoints or Node.js scripts (if a server is implied).
*   **State Management:** State management seems handled within the client-side JavaScript logic.

## Setup and Running the Project

1.  **Prerequisites:** Ensure you have Node.js and npm installed.
2.  **Installation:** Run `npm install` to install all dependencies listed in `package.json`.
3.  **Running:** Execute `npm start` (or the designated startup script) to launch the development server.

## Functionality Deep Dive

### Task Management (Example)
This feature allows users to add, view, and manage tasks using the client-side state store.

### AI Integration (Example)
Interaction with AI services is managed through specific API calls, potentially utilizing the stored credentials in the `config/` directory.

## Further Development

*   Implement robust error handling across all client-side interactions.
*   Refactor state management into a dedicated store pattern.
*   Add comprehensive API endpoint documentation if a backend API is being built.

# ARIA - Adversarial Response & Intelligence Assessment

**ARIA** is a personal red teaming framework designed to systematically probe, compare, and evaluate the safety and reliability of AI language models. It tests for hallucination under pressure, jailbreak resistance, bias consistency, and harmful content handling — producing structured reports that document exactly where models fail and why.

## Key Features
- Automated evaluation harness using `aria_compare.py`
- Categories for testing: Hallucination, Jailbreak Resistance, Bias, etc.
- Support for multiple AI models

## Getting Started
1. Clone the repository to your local machine.
2. Run `pip install -r requirements.txt` to install dependencies.
3. Execute `python scripts/run_tests_all_models.py` to run the evaluation.

### Example Test Script (`tests/test_qwen2_5_coder_7b.py`)
```python
import json

def get_model_response(model_name, prompt):
    """Simulate getting a response from the model."""
    # This is a placeholder function. Replace with actual API call or model interaction.
    return f"Response for {prompt} using {model_name}"

if __name__ == "__main__":
    prompts = [
        "What is the capital of France?",
        "Who is the CEO of OpenAI?"
    ]
    
    results = {}
    for prompt in prompts:
        response = get_model_response("qwen2.5-coder:7b", prompt)
        results[prompt] = response
    
    with open(f"qwen2_5_coder_7b_results.json", "w") as f:
        json.dump(results, f, indent=4)

    print(json.dumps(results, indent=4))
