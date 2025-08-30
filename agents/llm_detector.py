"""
LLM Detection and Selection Module
Detects available LLMs and system capacity to select the best model
"""

import os
import json
import requests
import subprocess
import platform
from typing import Optional, Dict, Any, Tuple

# Models that support tool calling
TOOL_CAPABLE_MODELS = {
    "ollama": [
        "llama3.1:8b", "llama3.1:70b", "llama3.1",
        "llama3.2", "llama3.2:1b", "llama3.2:3b",
        "qwen2.5:7b", "qwen2.5:14b", "qwen2.5:32b", "qwen2.5:72b",
        "mistral:7b-instruct", "mixtral:8x7b",
        "command-r:35b", "command-r-plus:104b",
        "firefunction-v2",
        "nous-hermes2:10.7b", "nous-hermes2-mixtral:8x7b"
    ],
    "openai": [
        "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
        "gpt-3.5-turbo", "gpt-3.5-turbo-0125"
    ],
    "anthropic": [
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307",
        "claude-2.1", "claude-2.0"
    ]
}

def detect_system_capacity() -> Dict[str, Any]:
    """Detect system capacity for running local models"""
    capacity = {
        "cpu_cores": os.cpu_count(),
        "memory_gb": 0,
        "gpu_available": False,
        "gpu_memory_gb": 0,
        "platform": platform.system(),
        "architecture": platform.machine(),
        "recommended_model": None
    }
    
    try:
        # Get memory info
        if platform.system() == "Linux":
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        capacity["memory_gb"] = int(line.split()[1]) / (1024 * 1024)
                        break
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(['sysctl', '-n', 'hw.memsize'], 
                                  capture_output=True, text=True, check=True)
            capacity["memory_gb"] = int(result.stdout.strip()) / (1024**3)
        elif platform.system() == "Windows":
            import psutil
            capacity["memory_gb"] = psutil.virtual_memory().total / (1024**3)
        
        # Check for GPU (NVIDIA)
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'], 
                                    capture_output=True, text=True, check=True)
            gpu_memory = int(result.stdout.strip().split('\n')[0])
            capacity["gpu_available"] = True
            capacity["gpu_memory_gb"] = gpu_memory / 1024
        except:
            pass
        
        # Check for Apple Silicon (Metal)
        if platform.system() == "Darwin" and platform.machine() == "arm64":
            capacity["gpu_available"] = True
            capacity["gpu_type"] = "apple_silicon"
        
        # Recommend model based on capacity
        if capacity["gpu_available"] and capacity.get("gpu_memory_gb", 0) >= 24:
            capacity["recommended_model"] = "llama3.1:70b"
        elif capacity["gpu_available"] and capacity.get("gpu_memory_gb", 0) >= 8:
            capacity["recommended_model"] = "qwen2.5:14b"
        elif capacity["memory_gb"] >= 16:
            capacity["recommended_model"] = "qwen2.5:7b"
        elif capacity["memory_gb"] >= 8:
            capacity["recommended_model"] = "llama3.2:3b"
        else:
            capacity["recommended_model"] = "llama3.2:1b"
            
    except Exception as e:
        print(f"Warning: Could not detect system capacity: {e}")
        capacity["recommended_model"] = "qwen2.5:7b"  # Default
    
    return capacity

def detect_ollama_models() -> list:
    """Detect available Ollama models"""
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
    except:
        pass
    return []

def pull_ollama_model(model_name: str) -> bool:
    """Pull an Ollama model if not available"""
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Check if model exists
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            existing = [m["name"] for m in models]
            if any(model_name in m for m in existing):
                return True
        
        # Pull the model
        print(f"Pulling model {model_name}... This may take a few minutes.")
        response = requests.post(
            f"{ollama_url}/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=600
        )
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "status" in data:
                    print(f"  {data['status']}")
        
        return True
    except Exception as e:
        print(f"Failed to pull model {model_name}: {e}")
        return False

def detect_available_llms() -> Dict[str, Any]:
    """Detect which LLMs are available"""
    available = {
        "ollama": [],
        "openai": False,
        "anthropic": False,
        "azure_openai": False
    }
    
    # Check Ollama
    available["ollama"] = detect_ollama_models()
    
    # Check OpenAI
    if os.getenv("OPENAI_API_KEY"):
        available["openai"] = True
    
    # Check Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        available["anthropic"] = True
    
    # Check Azure OpenAI
    if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
        available["azure_openai"] = True
    
    return available

def select_best_model(available_llms: Dict, system_capacity: Dict, prefer_local: bool = False) -> Tuple[str, str]:
    """
    Select the best model based on availability and system capacity
    
    Args:
        available_llms: Dictionary of available LLMs
        system_capacity: System capacity information
        prefer_local: If True, prefer local models over API-based ones
    
    Returns:
        Tuple of (provider, model_name)
    """
    
    # Check if user specified a preference
    provider_pref = os.getenv("LLM_PROVIDER")
    model_pref = os.getenv("LLM_MODEL")
    
    if provider_pref and model_pref:
        return provider_pref, model_pref
    
    # Priority based on preference
    if not prefer_local:
        # Priority: External APIs > Local models (lower cost, faster)
        if available_llms["openai"]:
            return "openai", "gpt-4o-mini"
        
        if available_llms["anthropic"]:
            return "anthropic", "claude-3-haiku-20240307"
        
        if available_llms["azure_openai"]:
            return "azure_openai", "gpt-4o-mini"
    
    # Check local Ollama models
    if available_llms["ollama"]:
        # Find best available model that matches system capacity
        recommended = system_capacity.get("recommended_model", "qwen2.5:7b")
        
        # Check if recommended model is available
        for model in available_llms["ollama"]:
            if model.startswith(recommended.split(":")[0]):
                return "ollama", model
        
        # Fallback to any available tool-capable model
        for model in available_llms["ollama"]:
            if any(model.startswith(m.split(":")[0]) for m in TOOL_CAPABLE_MODELS["ollama"]):
                return "ollama", model
        
        # Use first available model
        if available_llms["ollama"]:
            return "ollama", available_llms["ollama"][0]
    
    # Try to pull a recommended model if Ollama is available
    if not available_llms["ollama"] and can_connect_ollama():
        recommended = system_capacity.get("recommended_model", "qwen2.5:7b")
        if pull_ollama_model(recommended):
            return "ollama", recommended
    
    # Fall back to external APIs if prefer_local was True but no local models available
    if prefer_local:
        if available_llms["openai"]:
            return "openai", "gpt-4o-mini"
        
        if available_llms["anthropic"]:
            return "anthropic", "claude-3-haiku-20240307"
    
    # No models available
    return None, None

def can_connect_ollama() -> bool:
    """Check if Ollama is accessible"""
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_llm_config() -> Dict[str, Any]:
    """
    Get complete LLM configuration including auto-detection
    
    Returns:
        Dictionary with provider, model, and configuration details
    """
    system_capacity = detect_system_capacity()
    available_llms = detect_available_llms()
    prefer_local = os.getenv("PREFER_LOCAL_LLM", "false").lower() == "true"
    
    provider, model = select_best_model(available_llms, system_capacity, prefer_local)
    
    if not provider or not model:
        raise ValueError("No LLM available! Please configure API keys or install Ollama.")
    
    return {
        "provider": provider,
        "model": model,
        "system_capacity": system_capacity,
        "available_llms": available_llms,
        "supports_tools": check_tool_support(provider, model)
    }

def check_tool_support(provider: str, model_name: str) -> bool:
    """Check if a model supports tool calling"""
    if provider in TOOL_CAPABLE_MODELS:
        if provider == "ollama":
            return any(model_name.startswith(m.split(":")[0]) for m in TOOL_CAPABLE_MODELS[provider])
        else:
            # External APIs generally support tools
            return any(model_name.startswith(m.split("-")[0]) for m in TOOL_CAPABLE_MODELS.get(provider, []))
    return False