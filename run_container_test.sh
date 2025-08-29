#!/bin/bash

echo "======================================================================="
echo "Running Agent Tests in Docker Container"
echo "======================================================================="
echo "This script will:"
echo "1. Run tests inside a Docker container"
echo "2. Generate graphs inside the container"
echo "3. Save outputs to host directory via volume mount"
echo ""

# Create output directory on host if it doesn't exist
HOST_OUTPUT_DIR="$(pwd)/container_outputs"
mkdir -p "$HOST_OUTPUT_DIR"
echo "📁 Host output directory: $HOST_OUTPUT_DIR"
echo ""

# Run the container with volume mounts
echo "🐳 Starting Docker container..."
echo "-----------------------------------------------------------------------"

docker run --rm \
  --name test-agent-runner \
  -v "$(pwd):/app" \
  -v "$HOST_OUTPUT_DIR:/app/outputs" \
  -w /app \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e LLM_MODEL=qwen2.5:7b \
  -e OUTPUT_DIR=/app/outputs \
  -e PYTHONUNBUFFERED=1 \
  --add-host=host.docker.internal:host-gateway \
  python:3.11-slim \
  bash -c "
    echo '🔧 Installing dependencies (this may take a moment)...'
    pip install --quiet \
      langchain==0.3.27 \
      langgraph==0.6.6 \
      langsmith==0.4.20 \
      langchain-community==0.3.29 \
      langchain-ollama==0.3.7 \
      pandas \
      matplotlib \
      typer \
      requests
    
    echo ''
    echo '✅ Dependencies installed'
    echo ''
    echo '🚀 Running tests...'
    echo ''
    
    # Run the comprehensive test
    python docker_test_runner.py
    
    echo ''
    echo '📊 Running additional test with main.py...'
    python main.py test
  "

echo ""
echo "======================================================================="
echo "Container execution completed!"
echo "======================================================================="
echo ""
echo "📁 Output files are available at: $HOST_OUTPUT_DIR"
echo ""
echo "Files generated:"
ls -la "$HOST_OUTPUT_DIR"/*.png 2>/dev/null | awk '{print "   - "$9" ("$5" bytes)"}'
echo ""
echo "To view a graph, run:"
echo "   xdg-open $HOST_OUTPUT_DIR/container_regular_sales.png"
echo ""