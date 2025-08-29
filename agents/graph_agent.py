from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage
from tools.data_tools import profile_table, plot_chart

def build_graph():
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [profile_table, plot_chart]
    tool_node = ToolNode(tools)
    graph = StateGraph(dict)
    graph.add_node("llm", lambda s: {"messages":[model.invoke(s["messages"])]})
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", tools_condition, {"tools": "tools", "end": END})
    graph.add_edge("tools", "llm")
    return graph.compile()
