import os
import sys
import typer
from typing import Optional
from langchain_core.messages import HumanMessage

app = typer.Typer()

@app.command()
def run(prompt: str = "Analyze the sample data"):
    """Run the agent with a given prompt."""
    # Check for Ollama connection
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("LLM_MODEL", "llama3.2")
    
    # Test Ollama connection
    import requests
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code != 200:
            print(f"ERROR: Cannot connect to Ollama at {base_url}")
            print("Please ensure Ollama is running locally.")
            print("\nTo start Ollama: ollama serve")
            print(f"To pull the model: ollama pull {model_name}")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"ERROR: Cannot connect to Ollama at {base_url}")
        print("Please ensure Ollama is running locally.")
        print("\nTo start Ollama: ollama serve")
        print(f"To pull the model: ollama pull {model_name}")
        sys.exit(1)
    
    try:
        from agents.graph_agent import build_graph
        print(f"Starting agent with prompt: {prompt}")
        app_graph = build_graph()
        result = app_graph.invoke({"messages":[HumanMessage(content=prompt)]})
        print("\n=== Agent Response ===")
        print(result)
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running agent: {e}")
        sys.exit(1)

@app.command()
def chat():
    """Interactive chat mode with the agent."""
    # Check for Ollama connection
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("LLM_MODEL", "llama3.2")
    
    import requests
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code != 200:
            print(f"ERROR: Cannot connect to Ollama at {base_url}")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"ERROR: Cannot connect to Ollama at {base_url}")
        sys.exit(1)
    
    try:
        from agents.graph_agent import build_graph
        print("Starting interactive chat mode. Type 'exit' to quit.")
        app_graph = build_graph()
        
        while True:
            prompt = input("\n> ")
            if prompt.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            result = app_graph.invoke({"messages":[HumanMessage(content=prompt)]})
            print("\nAgent:", result)
    except Exception as e:
        print(f"Error in chat mode: {e}")
        sys.exit(1)

@app.command()
def sleep():
    """Keep the container running for interactive use."""
    print("=" * 50)
    print("LangGraph Table Agent - Interactive Mode")
    print("=" * 50)
    print("\nContainer is running and ready for commands.")
    print("Connect to this container to run commands:")
    print("  docker exec -it <container_id> python main.py chat")
    print("  docker exec -it <container_id> python main.py run 'your prompt'")
    print("\nPress Ctrl+C to stop the container.")
    print("=" * 50)
    
    # Keep the container running
    import time
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

@app.command()
def test():
    """Test if the agent is properly configured."""
    print("=" * 50)
    print("LangGraph Table Agent - Configuration Test")
    print("=" * 50)
    
    has_errors = False
    
    # Check Ollama connection
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("LLM_MODEL", "qwen2.5:7b")
    
    print(f"Configuration:")
    print(f"  Ollama URL: {base_url}")
    print(f"  Model: {model_name}")
    
    import requests
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running and accessible")
            # Check if model is available
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            if any(model_name in m for m in models):
                print(f"✓ Model {model_name} is available")
            else:
                print(f"⚠ Model {model_name} not found")
                print(f"  Available models: {', '.join(models) if models else 'none'}")
                print(f"  To pull model: ollama pull {model_name}")
                has_errors = True
            
            # Show tool-capable models that are available
            from agents.graph_agent import TOOL_CAPABLE_MODELS
            available_tool_models = [m for m in models if any(m.startswith(tc.split(':')[0]) for tc in TOOL_CAPABLE_MODELS)]
            if available_tool_models:
                print(f"\n  Tool-capable models available:")
                for m in available_tool_models:
                    print(f"    - {m}")
            else:
                print(f"\n  No tool-capable models found. Recommended:")
                print(f"    - qwen2.5:7b (default)")
                print(f"    - llama3.1:8b")
                print(f"    - llama3.2")
        else:
            print("⚠ Ollama is not responding correctly")
            has_errors = True
    except requests.exceptions.RequestException as e:
        print(f"⚠ Cannot connect to Ollama at {base_url}")
        print("  Make sure Ollama is running: ollama serve")
        has_errors = True
    
    # Check imports
    try:
        from agents.graph_agent import build_graph
        print("✓ Agent modules can be imported")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        has_errors = True
    
    # Check data directory
    if os.path.exists("/app/data"):
        print("✓ Data directory exists")
        files = os.listdir("/app/data")
        if files:
            print(f"  Found {len(files)} file(s): {', '.join(files)}")
    else:
        print("✓ Data directory created at /app/data")
    
    # Check output directory
    if os.path.exists("/app/outputs"):
        print("✓ Output directory exists")
    else:
        print("✓ Output directory created at /app/outputs")
    
    print("\n" + "=" * 50)
    if has_errors:
        print("⚠ Configuration incomplete - see warnings above")
        print("The agent needs Ollama running locally to function")
    else:
        print("✅ Agent is fully configured and ready to run!")
    print("=" * 50)
    
    # Don't exit with error code even if config is incomplete
    # This allows the container to stay running
    sys.exit(0)

if __name__ == "__main__":
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("LangGraph Table Agent")
        print("=====================")
        print("\nAvailable commands:")
        print("  run <prompt>  - Run agent with a specific prompt")
        print("  chat          - Start interactive chat mode")
        print("  test          - Test agent configuration")
        print("  sleep         - Keep container running for interactive use")
        print("\nExample: python main.py run 'Analyze the sales data'")
        print("\nFor interactive use in container:")
        print("  docker exec -it <container> python main.py chat")
        sys.exit(0)
    
    app()
