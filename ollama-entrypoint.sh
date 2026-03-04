#!/bin/bash
set -e

MODEL="${OLLAMA_MODEL:-mistral}"

# Start Ollama server in the background
ollama serve &
SERVER_PID=$!

# Wait for the server to become ready
echo "Waiting for Ollama to start..."
until ollama list > /dev/null 2>&1; do
    sleep 1
done

# Pull the model only if it isn't already present
if ollama list | grep -q "^${MODEL}"; then
    echo "Model '${MODEL}' already present, skipping pull."
else
    echo "Pulling model '${MODEL}'..."
    ollama pull "${MODEL}"
    echo "Model '${MODEL}' ready."
fi

# Hand control back to the server process
wait $SERVER_PID
