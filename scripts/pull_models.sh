#!/bin/sh
# Script to pull required Ollama models based on system capacity

echo "===================================================="
echo "Ollama Model Puller"
echo "===================================================="

# Wait for Ollama to be ready
sleep 5

# Function to pull a model
pull_model() {
    model=$1
    echo "Checking model: $model"
    
    # Check if model exists
    if ollama list | grep -q "$model"; then
        echo "✓ Model $model already exists"
    else
        echo "→ Pulling model $model..."
        ollama pull $model
        if [ $? -eq 0 ]; then
            echo "✓ Successfully pulled $model"
        else
            echo "✗ Failed to pull $model"
        fi
    fi
}

# Detect system memory (simplified for container)
MEMORY_GB=$(awk '/MemTotal/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)
echo "System memory: ${MEMORY_GB}GB"

# Select models based on available memory
if [ "$MEMORY_GB" -ge 32 ]; then
    echo "High memory system detected - pulling large models"
    pull_model "qwen2.5:14b"
    pull_model "llama3.1:8b"
elif [ "$MEMORY_GB" -ge 16 ]; then
    echo "Medium memory system detected - pulling medium models"
    pull_model "qwen2.5:7b"
    pull_model "llama3.2"
elif [ "$MEMORY_GB" -ge 8 ]; then
    echo "Low memory system detected - pulling small models"
    pull_model "llama3.2:3b"
    pull_model "qwen2.5:3b"
else
    echo "Very low memory system - pulling minimal models"
    pull_model "llama3.2:1b"
fi

# Always pull embedding model for RAG capabilities
pull_model "nomic-embed-text"

echo "===================================================="
echo "Model pulling complete!"
ollama list
echo "===================================================="