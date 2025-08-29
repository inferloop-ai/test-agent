# LangGraph Table Agent

An AI-powered agent for analyzing and visualizing table data using local Llama models via Ollama.

## Requirements

- **Ollama**: Must be running locally on your machine
- **Llama Model**: Default is `llama3.2`, configurable via environment variable

## Setup

### 1. Install and Start Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Pull the Llama model (in another terminal)
ollama pull llama3.2
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

The agent uses these environment variables:

- `OLLAMA_BASE_URL`: Ollama API endpoint (default: `http://localhost:11434`)
- `LLM_MODEL`: Model name to use (default: `llama3.2`)
- `OUTPUT_DIR`: Directory for output files (default: `/app/outputs`)

## Commands

### Test Configuration
```bash
python main.py test
```
Tests if the agent is properly configured (checks Ollama connection, model availability, data directory).

### Run with Prompt
```bash
python main.py run "Analyze the sales data"
```
Runs the agent with a specific prompt.

### Interactive Chat Mode
```bash
python main.py chat
```
Starts an interactive chat session with the agent.

## Docker Deployment

### Build the Image
```bash
docker build -t langgraph-table-agent:0.1.0 .
```

### Run the Container
```bash
# For Linux/Mac (using host.docker.internal)
docker run -e OLLAMA_BASE_URL=http://host.docker.internal:11434 langgraph-table-agent:0.1.0

# For custom Ollama URL
docker run -e OLLAMA_BASE_URL=http://your-ollama-host:11434 -e LLM_MODEL=llama3.2 langgraph-table-agent:0.1.0
```

## Available Models

You can use any model supported by Ollama:
- `llama3.2` (default, recommended)
- `llama3.1`
- `llama2`
- `mistral`
- `codellama`

To use a different model:
```bash
ollama pull mistral
export LLM_MODEL=mistral
python main.py run "Analyze the data"
```

## Troubleshooting

- **Connection Error**: Ensure Ollama is running (`ollama serve`)
- **Model Not Found**: Pull the model first (`ollama pull llama3.2`)
- **Docker Connection**: Use `host.docker.internal` on Mac/Windows, actual IP on Linux
- **Import Errors**: Install dependencies (`pip install -r requirements.txt`)