#!/bin/bash

echo "Testing Docker container with host Ollama..."

# For Linux, we need to get the host IP
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # On Linux, use the docker0 bridge IP or host network
    HOST_IP=$(ip -4 addr show docker0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "172.17.0.1")
    echo "Linux detected, using host IP: $HOST_IP"
    
    docker run --rm \
        --network host \
        -e LLM_MODEL=qwen2.5:7b \
        -e OLLAMA_BASE_URL=http://localhost:11434 \
        -v "$(pwd)/outputs:/app/outputs" \
        -v "$(pwd)/data:/app/data" \
        langgraph-table-agent:0.1.0 test
else
    # On Mac/Windows, use host.docker.internal
    docker run --rm \
        --add-host=host.docker.internal:host-gateway \
        -e LLM_MODEL=qwen2.5:7b \
        -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
        -v "$(pwd)/outputs:/app/outputs" \
        -v "$(pwd)/data:/app/data" \
        langgraph-table-agent:0.1.0 test
fi
