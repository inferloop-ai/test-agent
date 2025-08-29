from langchain_ollama import ChatOllama
from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage
from tools.data_tools import profile_table, plot_chart
import os

def build_graph():
    # Get configuration from environment variables
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("LLM_MODEL", "llama3.2")
    
    # Initialize Ollama with local Llama model
    model = ChatOllama(
        base_url=base_url,
        model=model_name,
        temperature=0
    )
    
    # Bind tools to the model
    tools = [profile_table, plot_chart]
    model_with_tools = model.bind_tools(tools)
    
    tool_node = ToolNode(tools)
    graph = StateGraph(dict)
    
    # Update to use model with bound tools
    graph.add_node("llm", lambda s: {"messages":[model_with_tools.invoke(s["messages"])]})
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", tools_condition, {"tools": "tools", "end": END})
    graph.add_edge("tools", "llm")
    
    return graph.compile()