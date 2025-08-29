#!/usr/bin/env python3
"""
Comprehensive test of qwen2.5:7b model with data analysis
"""
import os
import sys
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from tools.data_tools import profile_table, plot_chart

def test_qwen_model():
    # Configuration
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("LLM_MODEL", "qwen2.5:7b")
    output_dir = os.getenv("OUTPUT_DIR", "./outputs")
    
    print("=" * 70)
    print(f"  COMPREHENSIVE TEST: {model_name}")
    print("=" * 70)
    
    # Initialize model
    model = ChatOllama(
        base_url=base_url,
        model=model_name,
        temperature=0
    )
    
    # Test 1: Basic connectivity
    print("\n📡 TEST 1: Model Connectivity")
    print("-" * 40)
    try:
        response = model.invoke([HumanMessage(content="Say 'OK' if you're working")])
        print(f"✅ Model responded: {response.content[:100]}")
    except Exception as e:
        print(f"❌ Model connection failed: {e}")
        return False
    
    # Test 2: Data analysis understanding
    print("\n📊 TEST 2: Data Analysis Understanding")
    print("-" * 40)
    
    system_prompt = """You are a data analyst. You have CSV files available:
    - regular_sales.csv: Daily sales data with Date and Value columns
    - business_sales.csv: Business sales data with patterns
    Describe how you would analyze these files."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="What analysis would you perform on the regular_sales.csv file?")
    ]
    
    try:
        response = model.invoke(messages)
        print("Model's analysis approach:")
        print(response.content[:500] + "...")
    except Exception as e:
        print(f"❌ Analysis understanding failed: {e}")
        return False
    
    # Test 3: Tool execution - Profile Data
    print("\n🔧 TEST 3: Data Profiling Tool")
    print("-" * 40)
    
    try:
        # Test with regular sales data
        print("Profiling regular_sales.csv:")
        result = profile_table.invoke({"file": "data/regular_sales.csv"})
        stats = result.split('\\n')[:8]  # First 8 lines
        for line in stats:
            print(f"  {line}")
        print("✅ Profiling successful")
    except Exception as e:
        print(f"❌ Profiling failed: {e}")
        return False
    
    # Test 4: Tool execution - Create Chart
    print("\n📈 TEST 4: Visualization Tool")
    print("-" * 40)
    
    try:
        print("Creating chart from regular_sales.csv...")
        result = plot_chart.invoke({
            "file": "data/regular_sales.csv",
            "x": "Date",
            "y": "Value",
            "out": "qwen_test_comprehensive.png"
        })
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return False
    
    # Test 5: Complex reasoning
    print("\n🧠 TEST 5: Complex Business Reasoning")
    print("-" * 40)
    
    complex_prompt = """Based on the following sales statistics:
    - Average: $1,100/day
    - Peak day: Wednesday ($1,316)
    - Lowest day: Sunday ($773)
    - Annual growth: 20%
    
    What business recommendations would you make?"""
    
    try:
        response = model.invoke([HumanMessage(content=complex_prompt)])
        print("Model's recommendations:")
        print(response.content[:500] + "...")
        print("✅ Complex reasoning successful")
    except Exception as e:
        print(f"❌ Complex reasoning failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print("✅ All tests passed successfully!")
    print(f"✅ Model: {model_name}")
    print(f"✅ Data files processed: regular_sales.csv")
    print(f"✅ Visualizations created: qwen_test_comprehensive.png")
    
    return True

if __name__ == "__main__":
    success = test_qwen_model()
    sys.exit(0 if success else 1)