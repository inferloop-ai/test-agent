# Multi-LLM Support for LangGraph Table Agent

This agent now supports multiple LLM providers with automatic detection and selection based on availability and system capacity.

## Supported LLM Providers

### 1. Local Models (via Ollama)
- **Automatic model selection** based on system memory and GPU
- **Tool-capable models**: qwen2.5, llama3.1, llama3.2, mistral, mixtral
- **Auto-pulls** appropriate models in Docker setup

### 2. OpenAI API
- GPT-4, GPT-4 Turbo, GPT-4o
- GPT-3.5 Turbo
- Full tool/function calling support

### 3. Anthropic Claude API
- Claude 3 (Opus, Sonnet, Haiku)
- Claude 2.1, 2.0
- Full tool support

### 4. Azure OpenAI
- Same models as OpenAI
- Enterprise security and compliance

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start all services (Ollama + Agent)
docker-compose up -d

# View logs
docker-compose logs -f agent

# Run a test
docker-compose exec agent python main.py test

# Stop services
docker-compose down
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Test configuration
python test_llm_config.py

# Run agent
python main.py test
```

## Configuration

### Environment Variables

```bash
# Choose provider (auto-detects if not set)
LLM_PROVIDER=ollama|openai|anthropic|azure_openai
LLM_MODEL=qwen2.5:7b  # or gpt-4o-mini, claude-3-haiku, etc.

# Prefer local over cloud (cost savings)
PREFER_LOCAL_LLM=true

# API Keys (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://....openai.azure.com/
```

### Auto-Detection Logic

1. **System Capacity Detection**:
   - Detects CPU, RAM, GPU
   - Recommends appropriate model size

2. **LLM Availability Check**:
   - Checks for Ollama and installed models
   - Checks for configured API keys

3. **Model Selection Priority**:
   - With `PREFER_LOCAL_LLM=false`: Cloud APIs > Local models
   - With `PREFER_LOCAL_LLM=true`: Local models > Cloud APIs
   - Automatic fallback if preferred option unavailable

## System Requirements

### Minimum Requirements
- **Memory**: 4GB RAM (for small models)
- **CPU**: 4 cores
- **Storage**: 10GB free space

### Recommended by Model Size

| Model Size | RAM Required | Example Models |
|------------|-------------|----------------|
| 1-3B | 4-8 GB | llama3.2:1b, llama3.2:3b |
| 7B | 8-16 GB | qwen2.5:7b, mistral:7b |
| 14B | 16-32 GB | qwen2.5:14b |
| 70B | 64+ GB | llama3.1:70b |

### GPU Support
- NVIDIA GPUs automatically detected
- Apple Silicon (M1/M2/M3) supported
- GPU memory determines max model size

## Docker Compose Services

### 1. Ollama Server
- Runs Ollama for local models
- Auto-restarts on failure
- Persists models in volume

### 2. Model Puller
- Automatically pulls appropriate models
- Based on system capacity
- Runs once on startup

### 3. Agent
- Main LangGraph agent
- Auto-connects to Ollama or APIs
- Mounts data and output directories

### 4. Web UI (Optional)
- Open WebUI for Ollama
- Access at http://localhost:3000
- Enable with: `docker-compose --profile webui up`

## Testing

### Test LLM Configuration
```bash
# Test system detection and model selection
python test_llm_config.py

# Test with mock API keys
python test_llm_config.py --with-openai --with-anthropic
```

### Test Agent with Different Providers
```bash
# Test with Ollama
LLM_PROVIDER=ollama LLM_MODEL=qwen2.5:7b python main.py test

# Test with OpenAI
LLM_PROVIDER=openai LLM_MODEL=gpt-4o-mini python main.py test

# Test with Anthropic
LLM_PROVIDER=anthropic LLM_MODEL=claude-3-haiku-20240307 python main.py test
```

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# In Docker, check container
docker-compose ps ollama
docker-compose logs ollama
```

### Model Not Found
```bash
# Pull model manually
ollama pull qwen2.5:7b

# Or in Docker
docker-compose exec ollama ollama pull qwen2.5:7b
```

### API Key Issues
- Ensure API keys are set in `.env` or environment
- Check key format and validity
- Verify billing/credits available

### Memory Issues
- Reduce model size (e.g., use 3B instead of 7B)
- Increase Docker memory limits
- Use cloud APIs instead of local models

## Cost Optimization

1. **Use local models when possible** - Free after initial download
2. **Choose smaller cloud models** - gpt-4o-mini, claude-3-haiku
3. **Cache responses** - Avoid repeated API calls
4. **Set PREFER_LOCAL_LLM=true** - Prioritize free local models

## Advanced Configuration

### Custom Model Selection
```python
# In your code
from agents.llm_detector import select_best_model, detect_system_capacity

capacity = detect_system_capacity()
provider, model = select_best_model(
    available_llms,
    capacity,
    prefer_local=True
)
```

### Multi-Container Networking
```yaml
# docker-compose.override.yml
services:
  agent:
    networks:
      - agent-network
      - external-network
```

### GPU Acceleration
```yaml
# docker-compose.override.yml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```