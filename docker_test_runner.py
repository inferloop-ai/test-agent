#!/usr/bin/env python3
"""
Container test runner that generates graphs and saves them to host
"""
import os
import sys
import time
from datetime import datetime

def run_container_tests():
    print("=" * 70)
    print("CONTAINER TEST RUNNER - qwen2.5:7b")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Environment: Docker Container")
    print(f"Python: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Import tools
    try:
        from tools.data_tools import profile_table, plot_chart
        print("✅ Tools imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import tools: {e}")
        return False
    
    # Create output directory if needed
    output_dir = os.getenv("OUTPUT_DIR", "/app/outputs")
    os.makedirs(output_dir, exist_ok=True)
    print(f"✅ Output directory: {output_dir}")
    
    # Test datasets
    test_cases = [
        {
            "name": "Regular Sales Data",
            "file": "data/regular_sales.csv",
            "output": "container_regular_sales.png",
            "description": "Predictable patterns with weekly cycles"
        },
        {
            "name": "Business Sales Data",
            "file": "data/business_sales.csv",
            "output": "container_business_sales.png",
            "description": "Realistic business data with events"
        },
        {
            "name": "Example Sales Data",
            "file": "data/example_sales.csv",
            "output": "container_example_sales.png",
            "description": "Original random test data"
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"📊 Testing: {test['name']}")
        print(f"   Description: {test['description']}")
        print(f"   Input: {test['file']}")
        print(f"   Output: {test['output']}")
        print("-" * 40)
        
        try:
            # Profile the data
            start = time.time()
            profile_result = profile_table.invoke({"file": test["file"]})
            profile_time = time.time() - start
            
            # Show key statistics
            lines = profile_result.split('\n')
            print("📈 Statistics:")
            for line in lines[1:6]:  # Show first 5 lines after header
                print(f"   {line}")
            print(f"   ⏱️  Profiling time: {profile_time:.3f}s")
            
            # Create visualization
            start = time.time()
            output_path = os.path.join(output_dir, test["output"])
            chart_result = plot_chart.invoke({
                "file": test["file"],
                "x": "Date",
                "y": "Value",
                "out": test["output"]
            })
            viz_time = time.time() - start
            
            print(f"🎨 Visualization: {chart_result}")
            print(f"   ⏱️  Generation time: {viz_time:.3f}s")
            
            # Verify file exists
            full_path = os.path.join(output_dir, test["output"])
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path) / 1024  # KB
                print(f"   ✅ File created: {full_path} ({file_size:.1f} KB)")
                results.append({
                    "test": test["name"],
                    "status": "SUCCESS",
                    "file": test["output"],
                    "size_kb": file_size
                })
            else:
                print(f"   ❌ File not found: {full_path}")
                results.append({
                    "test": test["name"],
                    "status": "FAILED",
                    "error": "File not created"
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "test": test["name"],
                "status": "ERROR",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    print(f"✅ Successful: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("🎉 All tests passed!")
    
    print("\n📁 Generated Files:")
    for r in results:
        if r["status"] == "SUCCESS":
            print(f"   - {r['file']} ({r['size_kb']:.1f} KB)")
    
    print(f"\n📂 Output Directory: {output_dir}")
    print("   These files are accessible on the host via volume mount")
    
    # List all files in output directory
    print("\n📋 All files in output directory:")
    try:
        files = os.listdir(output_dir)
        for f in sorted(files):
            if f.endswith('.png'):
                path = os.path.join(output_dir, f)
                size = os.path.getsize(path) / 1024
                print(f"   - {f} ({size:.1f} KB)")
    except Exception as e:
        print(f"   Error listing files: {e}")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = run_container_tests()
    sys.exit(0 if success else 1)