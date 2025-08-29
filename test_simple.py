#!/usr/bin/env python3
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# Test basic connection
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model_name = os.getenv("LLM_MODEL", "llama3.2")

print(f"Testing connection to {base_url} with model {model_name}")

model = ChatOllama(
    base_url=base_url,
    model=model_name,
    temperature=0
)

# Test simple message
response = model.invoke([HumanMessage(content="Say hello")])
print(f"Response: {response.content}")