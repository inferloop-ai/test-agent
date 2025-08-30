# Web UI Guide for LangGraph Table Agent

## Understanding the Components

### 1. **Agent Web UI (Port 8000)**
- **What**: Custom web interface for the LangGraph agent
- **Purpose**: Interact with the data analysis agent
- **Features**: Analyze CSV files, create charts, statistical analysis

### 2. **Ollama Web UI (Port 3000)** - Optional
- **What**: Open WebUI for direct Ollama chat
- **Purpose**: General chat with LLM models
- **Note**: Does NOT have access to agent tools

## Quick Start

### Start Everything with Docker Compose:

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Access the Agent Web UI
open http://localhost:8000
```

## Using the Agent Web UI

### Available Commands in Chat:

1. **Data Discovery**:
   - "What data files are available?"
   - "List the CSV files"
   - "Show me the data"

2. **Data Analysis**:
   - "Analyze the sales data"
   - "Profile business_sales.csv"
   - "Show statistics for regular_sales.csv"

3. **Visualizations**:
   - "Create a chart showing sales trends"
   - "Plot Date vs Value from business_sales.csv"
   - "Generate a line graph of monthly sales"

4. **Complex Queries**:
   - "Analyze business_sales.csv and identify seasonal patterns"
   - "Compare regular sales with business sales"
   - "What are the peak sales periods?"

## Using CLI Inside Container

If you need command-line access:

```bash
# Run test
docker-compose exec agent python main.py test

# Start CLI chat
docker-compose exec agent python main.py chat

# Run specific command
docker-compose exec agent python main.py run "Analyze the sales data"

# Get shell access
docker-compose exec agent bash

# Then inside container:
python main.py test
python main.py chat
python main.py run "What data files are available?"
```

## Troubleshooting

### Web UI Not Responding

1. **Check if services are running**:
```bash
docker-compose ps
```

2. **Check agent logs**:
```bash
docker-compose logs agent
```

3. **Check Ollama connection**:
```bash
docker-compose logs ollama
```

4. **Restart services**:
```bash
docker-compose restart
```

### "Agent not initialized" Error

This means the LLM connection failed:

```bash
# Check Ollama is running
docker-compose exec ollama ollama list

# Pull required model
docker-compose exec ollama ollama pull qwen2.5:7b

# Restart agent
docker-compose restart agent
```

### Can't Connect to Web UI

1. **Check port 8000 is free**:
```bash
lsof -i :8000
```

2. **Check firewall/iptables**:
```bash
sudo iptables -L -n | grep 8000
```

3. **Try direct connection**:
```bash
curl http://localhost:8000/health
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Browser       │────▶│  Agent Web UI   │
│                 │     │  (Port 8000)    │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  LangGraph      │
                        │    Agent        │
                        └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           ┌─────────────────┐      ┌─────────────────┐
           │     Ollama      │      │   External API  │
           │  (Local LLM)    │      │ (OpenAI/Claude) │
           └─────────────────┘      └─────────────────┘
```

## Features

### Web UI Features:
- ✅ Real-time chat interface
- ✅ WebSocket connection for streaming
- ✅ Automatic chart display
- ✅ Markdown formatting
- ✅ Error handling
- ✅ Connection status

### Agent Capabilities:
- ✅ CSV file analysis
- ✅ Statistical profiling
- ✅ Chart generation
- ✅ Multi-LLM support
- ✅ Tool calling
- ✅ Auto model selection

## Configuration

### Environment Variables:
Edit `.env` file to configure:

```bash
# Choose LLM provider
LLM_PROVIDER=ollama  # or openai, anthropic
LLM_MODEL=qwen2.5:7b

# API Keys (if using cloud LLMs)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Change Web UI Port:
In `docker-compose.yml`:
```yaml
agent:
  ports:
    - "9000:8000"  # Change 9000 to your desired port
```

## Advanced Usage

### Custom Data:
Add CSV files to the `data/` directory:
```bash
cp mydata.csv data/
docker-compose restart agent
```

### View Generated Charts:
Charts are saved in `outputs/`:
```bash
ls outputs/
open outputs/chart_*.png
```

### Direct API Access:
```python
import requests
import json

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# WebSocket connection for chat
# See web_app.py for WebSocket protocol
```

## Tips

1. **Use specific file names**: "Analyze business_sales.csv" instead of "Analyze the data"
2. **Request specific chart types**: "Create a line chart" or "Make a bar graph"
3. **Ask for comparisons**: "Compare Q1 and Q2 sales"
4. **Export results**: Charts are automatically saved to `outputs/`

## Security Notes

- The web UI binds to 0.0.0.0:8000 (accessible from network)
- For local-only access, modify docker-compose.yml:
  ```yaml
  ports:
    - "127.0.0.1:8000:8000"
  ```
- Always use environment variables for API keys
- Don't expose ports unnecessarily