#!/bin/bash

echo "Running agent in Docker container..."
echo "=================================="

# Run the agent test in a container using the virtual environment from host
docker run --rm \
  -v /home/dmiruke/test-agent:/workspace \
  -w /workspace \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e LLM_MODEL=qwen2.5:7b \
  -e OUTPUT_DIR=./outputs \
  --add-host=host.docker.internal:host-gateway \
  python:3.11 \
  bash -c "
    echo 'Container Environment:';
    echo '  Hostname:' \$(hostname);
    echo '  Working Dir:' \$(pwd);
    echo '  Python:' \$(which python);
    echo '';
    echo 'Installing dependencies...';
    pip install -q langchain langgraph langsmith langchain-community langchain-ollama pandas matplotlib typer requests;
    echo '';
    echo 'Running agent test...';
    echo '====================';
    python main.py test;
    echo '';
    echo 'Testing data analysis...';
    python -c \"
from tools.data_tools import profile_table, plot_chart
print('Analyzing regular_sales.csv from container:')
result = profile_table.invoke({'file': 'data/regular_sales.csv'})
print(result[:300])
    \"
  "