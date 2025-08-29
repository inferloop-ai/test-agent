#!/usr/bin/env python3
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from tools.data_tools import profile_table, plot_chart

# Setup
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model_name = os.getenv("LLM_MODEL", "llama3.2")

model = ChatOllama(
    base_url=base_url,
    model=model_name,
    temperature=0
)

print("Testing agent with manual tool execution...")

# System prompt explaining available tools
system_prompt = """You are a data analysis assistant. You have access to analyze CSV files.
When asked to analyze data, describe what analysis you would perform.
Available data files: example_sales.csv (contains Date and Sales columns)"""

# Get user request
user_prompt = "Analyze the sales data and create a visualization"

messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=user_prompt)
]

# Get model response
print(f"\nUser: {user_prompt}")
response = model.invoke(messages)
print(f"\nAssistant: {response.content}")

# Manually execute tools based on the request
print("\n--- Executing Data Analysis ---")

# Profile the data
print("\n1. Profiling the data:")
profile_result = profile_table.invoke({"file": "data/example_sales.csv"})
print(profile_result)

# Create a chart
print("\n2. Creating visualization:")
chart_result = plot_chart.invoke({"file": "data/example_sales.csv", "x": "Date", "y": "Value"})
print(chart_result)

print("\nAnalysis complete!")