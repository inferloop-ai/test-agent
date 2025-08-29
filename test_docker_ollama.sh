#!/bin/bash

echo "===================================================="
echo "Testing Docker Container with Host Ollama"
echo "===================================================="

# Check if Ollama is running on host
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running on host. Please start with: ollama serve"
    exit 1
fi

echo "✅ Ollama is running on host"

# Build the container (use cached layers if available)
echo "Building Docker image..."
docker build -t langgraph-table-agent:test . || {
    echo "❌ Docker build failed"
    exit 1
}

echo "✅ Docker image built"

# Run the container with host network access
echo ""
echo "Running container test..."
echo "===================================================="

docker run --rm \
    --add-host=host.docker.internal:host-gateway \
    -e LLM_MODEL=qwen2.5:7b \
    -v "$(pwd)/outputs:/app/outputs" \
    -v "$(pwd)/data:/app/data" \
    langgraph-table-agent:test

echo ""
echo "===================================================="
echo "Container test complete!"
echo "===================================================="