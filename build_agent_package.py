#!/usr/bin/env python3
"""
Build a portable agent package for deployment
Creates a minimal zip file with only required runtime files
"""

import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def build_agent_package():
    """Build portable agent zip package"""
    
    # Define package name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"langgraph-agent-{timestamp}.zip"
    
    # Files and directories to include
    include_patterns = [
        # Core application files
        "main.py",
        "agents/",
        "tools/",
        
        # Configuration files
        "requirements.txt",
        "agent.yaml",
        "Dockerfile",
        
        # Data directory structure (empty)
        "data/",
    ]
    
    # Files to explicitly exclude
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        "venv/",
        "env/",
        "outputs/",
        "container_outputs/",
        "*.png",
        "*.jpg",
        "test_*.py",
        "generate_*.py",
        "docker_test_runner.py",
        "*.sh",
        "*.md",
        "*.log",
        "*.zip",
        ".dockerignore",
        ".gitignore",
        "build_agent_package.py",  # Don't include this script
    ]
    
    def should_include(path):
        """Check if file should be included"""
        path_str = str(path)
        
        # Check excludes first
        for pattern in exclude_patterns:
            if pattern.endswith("/"):
                if pattern in path_str:
                    return False
            elif pattern.startswith("*."):
                if path_str.endswith(pattern[1:]):
                    return False
            elif pattern in path_str:
                return False
        
        return True
    
    print(f"Building agent package: {package_name}")
    print("=" * 50)
    
    included_files = []
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pattern in include_patterns:
            if pattern.endswith("/"):
                # Directory - walk through it
                dir_path = Path(pattern)
                if dir_path.exists():
                    for file_path in dir_path.rglob("*"):
                        if file_path.is_file() and should_include(file_path):
                            arcname = str(file_path)
                            zipf.write(file_path, arcname)
                            included_files.append(arcname)
                            print(f"  + {arcname}")
                else:
                    # Create empty directory in zip
                    zipf.writestr(f"{pattern}", "")
                    print(f"  + {pattern} (empty directory)")
            else:
                # Single file or glob pattern
                path = Path(pattern)
                if path.exists() and path.is_file():
                    if should_include(path):
                        zipf.write(path, str(path))
                        included_files.append(str(path))
                        print(f"  + {path}")
    
    # Get package size
    package_size = os.path.getsize(package_name)
    size_mb = package_size / (1024 * 1024)
    
    print("=" * 50)
    print(f"✅ Package created: {package_name}")
    print(f"📦 Size: {size_mb:.2f} MB")
    print(f"📁 Files included: {len(included_files)}")
    
    # Create a manifest file
    manifest_name = f"manifest-{timestamp}.txt"
    with open(manifest_name, 'w') as f:
        f.write(f"Agent Package Manifest\n")
        f.write(f"Package: {package_name}\n")
        f.write(f"Created: {datetime.now().isoformat()}\n")
        f.write(f"Size: {size_mb:.2f} MB\n")
        f.write(f"Files: {len(included_files)}\n")
        f.write("\nIncluded files:\n")
        f.write("-" * 40 + "\n")
        for file in sorted(included_files):
            f.write(f"{file}\n")
    
    print(f"📋 Manifest created: {manifest_name}")
    
    # Print deployment instructions
    print("\n" + "=" * 50)
    print("Deployment Instructions:")
    print("-" * 50)
    print("1. Upload the zip file to your deployment environment")
    print("2. Extract: unzip " + package_name)
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Set environment variables:")
    print("   export OLLAMA_BASE_URL=http://localhost:11434")
    print("   export LLM_MODEL=qwen2.5:7b")
    print("5. Run: python main.py test")
    print("\nFor Docker deployment:")
    print("1. Extract the zip file")
    print("2. Build: docker build -t langgraph-agent .")
    print("3. Run: docker run --rm langgraph-agent")
    
    return package_name, manifest_name

if __name__ == "__main__":
    package, manifest = build_agent_package()