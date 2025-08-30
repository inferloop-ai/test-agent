from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage
from tools.data_tools import profile_table, plot_chart
from agents.llm_detector import get_llm_config, detect_system_capacity, detect_available_llms
from agents.llm_factory import get_llm_instance
import os

def build_graph():
    """Build the LangGraph agent with auto-detected or configured LLM"""
    
    # Get LLM configuration
    try:
        config = get_llm_config()
        provider = config["provider"]
        model_name = config["model"]
        supports_tools = config["supports_tools"]
        
        # Display configuration info
        print("=" * 50)
        print("LLM Configuration:")
        print(f"  Provider: {provider}")
        print(f"  Model: {model_name}")
        print(f"  Tool Support: {'Yes' if supports_tools else 'No'}")
        
        system_cap = config["system_capacity"]
        print(f"\nSystem Capacity:")
        print(f"  CPU Cores: {system_cap['cpu_cores']}")
        print(f"  Memory: {system_cap['memory_gb']:.1f} GB")
        if system_cap['gpu_available']:
            print(f"  GPU: Yes ({system_cap.get('gpu_type', 'NVIDIA')})")
            if 'gpu_memory_gb' in system_cap:
                print(f"  GPU Memory: {system_cap['gpu_memory_gb']:.1f} GB")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error detecting LLM configuration: {e}")
        # Fall back to manual configuration
        provider = os.getenv("LLM_PROVIDER", "ollama")
        model_name = os.getenv("LLM_MODEL", "qwen2.5:7b")
        supports_tools = True
    
    # Get the LLM instance
    model = get_llm_instance(provider, model_name)
    
    # Bind tools to the model
    tools = [profile_table, plot_chart]
    
    if not supports_tools:
        print(f"Warning: Model {model_name} may not support tool calling.")
        model_with_tools = model
    else:
        try:
            model_with_tools = model.bind_tools(tools)
        except Exception as e:
            print(f"Warning: Could not bind tools to {model_name}: {e}")
            print("The model will run without tool support.")
            model_with_tools = model
    
    # Build the graph
    tool_node = ToolNode(tools)
    graph = StateGraph(dict)
    
    graph.add_node("llm", lambda s: {"messages": [model_with_tools.invoke(s["messages"])]})
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "llm")
    
    return graph.compile()