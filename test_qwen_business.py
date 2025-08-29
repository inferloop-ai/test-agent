#!/usr/bin/env python3
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from tools.data_tools import profile_table, plot_chart

# Setup
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model_name = "qwen2.5:7b"

model = ChatOllama(
    base_url=base_url,
    model=model_name,
    temperature=0
)

print(f"Testing {model_name} with realistic business sales data...")
print("=" * 60)

# System prompt
system_prompt = """You are a business data analyst. You have access to analyze CSV files and create visualizations.
Available data files: 
- business_sales.csv: Daily sales data for 2024 with Date and Value columns
- business_sales_detailed.csv: Same data with additional metadata (Day_of_Week, Month, Quarter)

When asked to analyze data, provide insights about trends, patterns, and anomalies."""

# User request
user_prompt = "Analyze the business sales data and identify key patterns, trends, and notable events"

messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=user_prompt)
]

# Get model response
print(f"\nUser: {user_prompt}")
print("\n" + "=" * 60)
response = model.invoke(messages)
print(f"\nAssistant Analysis:\n{response.content}")

# Execute tools
print("\n" + "=" * 60)
print("\n📊 Executing Data Analysis Tools...")
print("-" * 40)

# Profile the data
print("\n1. Statistical Profile of Business Sales:")
profile_result = profile_table.invoke({"file": "data/business_sales.csv"})
print(profile_result)

# Create visualization
print("\n2. Creating Sales Trend Visualization:")
chart_result = plot_chart.invoke({
    "file": "data/business_sales.csv", 
    "x": "Date", 
    "y": "Value",
    "out": "qwen_business_analysis.png"
})
print(chart_result)

# Analyze detailed data
print("\n3. Analyzing Detailed Business Data:")
detailed_profile = profile_table.invoke({"file": "data/business_sales_detailed.csv"})
print(detailed_profile)

print("\n" + "=" * 60)
print("✅ Analysis complete with qwen2.5:7b model!")