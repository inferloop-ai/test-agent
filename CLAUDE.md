# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangGraph-based AI agent for table data analysis, built with Python 3.11 and containerized with Docker. The agent uses OpenAI's GPT-4o-mini model to analyze CSV data and generate visualizations.

## Common Development Commands

### Running the Application
```bash
# Test configuration
python main.py test

# Run with specific prompt
python main.py run "Analyze the sales data and create a chart"

# Interactive chat mode
python main.py chat

# Docker build
docker build -t langgraph-table-agent:0.1.0 .

# Docker run
docker run -e OPENAI_API_KEY=your_key langgraph-table-agent:0.1.0
```

### Testing
No test framework is currently configured. When implementing tests, consider adding pytest to requirements.txt.

## Architecture

The application follows a tool-based AI agent pattern:

1. **Entry Point** (`main.py`): Typer CLI that routes commands to the agent
2. **Agent Core** (`agents/graph_agent.py`): LangGraph StateGraph implementation that:
   - Manages conversation state and tool execution
   - Uses ChatOpenAI with gpt-4o-mini model
   - Implements conditional routing between LLM and tool execution
3. **Tools** (`tools/data_tools.py`): Data processing capabilities:
   - `profile_table()`: Statistical analysis of CSV files
   - `plot_chart()`: Generate matplotlib visualizations
   - All outputs saved to `/app/outputs/` directory

The agent processes CSV files from the `data/` directory and can perform statistical profiling and create visualizations based on natural language requests.

## Important Implementation Notes

- **Security Issue**: The Dockerfile contains a hardcoded OpenAI API key on line 13. This should be removed and passed as an environment variable instead.
- **Environment Variables**: 
  - `OPENAI_API_KEY` (required)
  - `OUTPUT_DIR` (optional, defaults to `/app/outputs`)
- **Data Flow**: CSV files → Pandas processing → Matplotlib visualizations → Output directory
- **Model Configuration**: Uses `gpt-4o-mini` with temperature 0 for consistent results
- **Container Paths**: `/app/data/` for input files, `/app/outputs/` for generated content