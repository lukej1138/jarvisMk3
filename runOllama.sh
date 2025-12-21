#!/bin/bash
set -euo pipefail
# start ollama server in background
ollama serve &

until curl -s http://localhost:11434 >/dev/null; do
  echo "Waiting for Ollama to be ready..."
  sleep 1
done

echo -e "Ollama server ready! Pulling and creating model..."

# pull/create model (adjust names as needed)
ollama pull dolphin-mistral:7b-v2.6-q4_K_M || true
ollama create jarvisMk3 -f Modelfile || true

echo -e "Model setup complete! Starting Flask server..."

echo -e "Starting Python server..."
exec python3 ClassifierServer.py