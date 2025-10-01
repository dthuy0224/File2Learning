#!/bin/sh
# init-ollama.sh

# Bắt đầu service Ollama ở chế độ nền
/bin/ollama serve &

# Lấy PID của tiến trình nền
PID=$!

echo "Ollama service started with PID: $PID"
echo "Waiting for Ollama to be ready..."

# Chờ một chút để service có thời gian khởi động
sleep 5

echo "Pulling required AI model: llama2:7b..."
echo "This may take a few minutes depending on your internet connection."

# Tải model mặc định
/bin/ollama pull llama2:7b

echo "Model pull complete."
echo "Ollama is now ready with the required models."

# Đưa tiến trình nền trở lại foreground để container tiếp tục chạy
wait $PID
