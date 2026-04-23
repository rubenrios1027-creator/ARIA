#!/bin/bash
# Hermes Model Switcher
# Usage: ./hermes-model-switch.sh

CONFIG="$HOME/.hermes/config.yaml"
HOST="http://172.21.32.1:11434/v1"

echo ""
echo "⚕  Hermes Model Switcher"
echo "─────────────────────────"
echo "Available models:"
echo ""
echo "  1) gemma4:latest       (9.6GB - powerful, slower)"
echo "  2) hermes3:8b          (4.7GB - fast, smart)"
echo "  3) llama3.1:8b         (4.9GB - fast, well-rounded)"
echo "  4) qwen2.5-coder:7b    (4.7GB - great for code)"
echo "  5) qwen2.5-coder:14b   (9.0GB - best for code)"
echo "  6) mistral:latest      (4.4GB - fast, reliable)"
echo "  7) qwen3.5:latest      (6.6GB - balanced)"
echo ""
read -p "Pick a number (1-7): " choice

case $choice in
  1) MODEL="gemma4:latest" ;;
  2) MODEL="hermes3:8b" ;;
  3) MODEL="llama3.1:8b" ;;
  4) MODEL="qwen2.5-coder:7b" ;;
  5) MODEL="qwen2.5-coder:14b" ;;
  6) MODEL="mistral:latest" ;;
  7) MODEL="qwen3.5:latest" ;;
  *) echo "Invalid choice. Exiting."; exit 1 ;;
esac

# Update line 3 (default) and line 4 (base_url) in config
sed -i "3s|default:.*|default: $MODEL|" "$CONFIG"
sed -i "4s|base_url:.*|base_url: $HOST|" "$CONFIG"

echo ""
echo "✅ Switched to: $MODEL"
echo "🚀 Run 'hermes' to start!"
echo ""
