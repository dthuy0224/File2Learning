#!/bin/sh
# init-ollama.sh

# Start Ollama service in background
/bin/ollama serve &

# Get PID of background process
PID=$!

echo "Ollama service started with PID: $PID"
echo "Waiting for Ollama to be ready..."

# Wait a bit for service to have time to start up
sleep 5

echo "Pulling required AI model: llama2:7b..."
echo "This may take a few minutes depending on your internet connection."

# Download default model
/bin/ollama pull llama2:7b

echo "Model pull complete."
echo "Ollama is now ready with the required models."

# Bring background process back to foreground so container continues running
wait $PID
