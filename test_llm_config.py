#!/usr/bin/env python3
"""
Test script for LLM configuration detection and selection
"""

import os
import sys
from agents.llm_detector import (
    detect_system_capacity,
    detect_available_llms,
    select_best_model,
    get_llm_config,
    pull_ollama_model
)
from agents.llm_factory import get_llm_instance

def test_system_detection():
    """Test system capacity detection"""
    print("=" * 60)
    print("SYSTEM CAPACITY DETECTION")
    print("=" * 60)
    
    capacity = detect_system_capacity()
    
    print(f"Platform: {capacity['platform']} ({capacity['architecture']})")
    print(f"CPU Cores: {capacity['cpu_cores']}")
    print(f"Memory: {capacity['memory_gb']:.2f} GB")
    print(f"GPU Available: {capacity['gpu_available']}")
    
    if capacity['gpu_available']:
        if 'gpu_memory_gb' in capacity:
            print(f"GPU Memory: {capacity['gpu_memory_gb']:.2f} GB")
        if 'gpu_type' in capacity:
            print(f"GPU Type: {capacity['gpu_type']}")
    
    print(f"\nRecommended Model: {capacity['recommended_model']}")
    return capacity

def test_llm_detection():
    """Test LLM availability detection"""
    print("\n" + "=" * 60)
    print("LLM AVAILABILITY DETECTION")
    print("=" * 60)
    
    available = detect_available_llms()
    
    print("\nLocal Models (Ollama):")
    if available['ollama']:
        for model in available['ollama']:
            print(f"  - {model}")
    else:
        print("  No Ollama models found (Ollama may not be running)")
    
    print("\nExternal APIs:")
    print(f"  OpenAI: {'✓ Configured' if available['openai'] else '✗ Not configured'}")
    print(f"  Anthropic: {'✓ Configured' if available['anthropic'] else '✗ Not configured'}")
    print(f"  Azure OpenAI: {'✓ Configured' if available['azure_openai'] else '✗ Not configured'}")
    
    return available

def test_model_selection(available, capacity):
    """Test model selection logic"""
    print("\n" + "=" * 60)
    print("MODEL SELECTION")
    print("=" * 60)
    
    # Test with prefer_local = False (prefer APIs)
    print("\nPrefer APIs over local models:")
    provider, model = select_best_model(available, capacity, prefer_local=False)
    if provider:
        print(f"  Selected: {provider}/{model}")
    else:
        print("  No suitable model found")
    
    # Test with prefer_local = True
    print("\nPrefer local models over APIs:")
    provider, model = select_best_model(available, capacity, prefer_local=True)
    if provider:
        print(f"  Selected: {provider}/{model}")
    else:
        print("  No suitable model found")
    
    return provider, model

def test_llm_instance(provider, model):
    """Test LLM instance creation"""
    print("\n" + "=" * 60)
    print("LLM INSTANCE TEST")
    print("=" * 60)
    
    if not provider or not model:
        print("No model available for testing")
        return
    
    print(f"Creating instance: {provider}/{model}")
    
    try:
        llm = get_llm_instance(provider, model)
        print("✓ LLM instance created successfully")
        
        # Test basic invocation
        print("\nTesting basic invocation...")
        response = llm.invoke("Say 'Hello, World!' and nothing else.")
        print(f"Response: {response.content}")
        print("✓ Basic invocation successful")
        
    except Exception as e:
        print(f"✗ Failed to create/test LLM instance: {e}")

def test_full_config():
    """Test full configuration flow"""
    print("\n" + "=" * 60)
    print("FULL CONFIGURATION TEST")
    print("=" * 60)
    
    try:
        config = get_llm_config()
        
        print(f"Provider: {config['provider']}")
        print(f"Model: {config['model']}")
        print(f"Tool Support: {config['supports_tools']}")
        
        return config
    except Exception as e:
        print(f"Configuration failed: {e}")
        return None

def main():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("LLM CONFIGURATION TEST SUITE")
    print("*" * 60)
    
    # Set test environment variables if needed
    if "--with-openai" in sys.argv:
        os.environ["OPENAI_API_KEY"] = "test-key"
        print("Note: Testing with mock OpenAI key")
    
    if "--with-anthropic" in sys.argv:
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        print("Note: Testing with mock Anthropic key")
    
    # Run tests
    capacity = test_system_detection()
    available = test_llm_detection()
    provider, model = test_model_selection(available, capacity)
    
    # Only test instance if we have real credentials
    if provider and model and not ("test-key" in os.environ.get("OPENAI_API_KEY", "") or 
                                   "test-key" in os.environ.get("ANTHROPIC_API_KEY", "")):
        test_llm_instance(provider, model)
    
    # Test full config
    config = test_full_config()
    
    print("\n" + "*" * 60)
    print("TEST COMPLETE")
    print("*" * 60)
    
    # Provide recommendations
    print("\nRECOMMENDATIONS:")
    
    if not available['ollama'] and capacity['memory_gb'] >= 8:
        print("• Install Ollama for local LLM support: https://ollama.ai")
        print(f"• Recommended model for your system: {capacity['recommended_model']}")
    
    if not available['openai'] and not available['anthropic']:
        print("• Consider configuring OpenAI or Anthropic API keys for cloud LLM access")
    
    if available['ollama'] and len(available['ollama']) == 0:
        print(f"• Pull recommended model: ollama pull {capacity['recommended_model']}")

if __name__ == "__main__":
    main()