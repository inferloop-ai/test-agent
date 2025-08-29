from langchain_ollama import ChatOllama
from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage
from tools.data_tools import profile_table, plot_chart
import os

# Models that support tool calling
TOOL_CAPABLE_MODELS = [
    "llama3.1:8b", "llama3.1:70b", "llama3.1",
    "llama3.2", "llama3.2:1b", "llama3.2:3b",
    "qwen2.5:7b", "qwen2.5:14b", "qwen2.5:32b", "qwen2.5:72b",
    "mistral:7b-instruct", "mixtral:8x7b",
    "command-r:35b", "command-r-plus:104b",
    "firefunction-v2",
    "nous-hermes2:10.7b", "nous-hermes2-mixtral:8x7b"
]

def build_graph():
    # Get configuration from environment variables
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("LLM_MODEL", "qwen2.5:7b")  # Default to qwen2.5:7b
    
    # Check if model supports tools
    supports_tools = any(model_name.startswith(m.split(":")[0]) for m in TOOL_CAPABLE_MODELS)
    
    if not supports_tools:
        print(f"Warning: Model {model_name} may not support tool calling.")
        print(f"Recommended models: {', '.join(TOOL_CAPABLE_MODELS[:5])}...")
    
    # Initialize Ollama with the selected model
    model = ChatOllama(
        base_url=base_url,
        model=model_name,
        temperature=0
    )
    
    # Bind tools to the model
    tools = [profile_table, plot_chart]
    
    try:
        model_with_tools = model.bind_tools(tools)
    except Exception as e:
        print(f"Warning: Could not bind tools to {model_name}: {e}")
        print("The model will run without tool support.")
        model_with_tools = model
    
    tool_node = ToolNode(tools)
    graph = StateGraph(dict)
    
    # Update to use model with bound tools
    graph.add_node("llm", lambda s: {"messages":[model_with_tools.invoke(s["messages"])]})
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "llm")
    
    return graph.compile()