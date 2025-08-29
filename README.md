# LangGraph Table Agent

An AI-powered agent for analyzing and visualizing table data using OpenAI GPT-4.

## Requirements

- **OPENAI_API_KEY**: Required environment variable for OpenAI API access

## Commands

### Test Configuration
```bash
python main.py test
```
Tests if the agent is properly configured (checks API key, imports, data directory).

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

## Deployment

When deploying this agent, make sure to provide the OPENAI_API_KEY:

1. **Via AgentCraft UI**: Add OPENAI_API_KEY in the environment variables section when uploading
2. **Via Docker**: 
   ```bash
   docker run -e OPENAI_API_KEY=your_key agent_image
   ```

## Default Behavior

If no command is provided, the agent will show available commands.
If deployed without arguments, it will run the `test` command to verify configuration.

## Troubleshooting

- **Exit Code 1**: Usually means OPENAI_API_KEY is not set
- **Import Errors**: Dependencies not installed properly
- **No Data**: Check if data files are mounted/copied correctly