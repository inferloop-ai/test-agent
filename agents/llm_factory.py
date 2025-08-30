"""
LLM Factory Module
Creates appropriate LLM instances based on provider configuration
"""

import os
from typing import Any, Optional

def get_llm_instance(provider: str, model_name: str, **kwargs):
    """
    Get LLM instance based on provider and model
    
    Args:
        provider: LLM provider (ollama, openai, anthropic, azure_openai)
        model_name: Model name
        **kwargs: Additional parameters for the LLM
    
    Returns:
        LLM instance
    """
    
    temperature = kwargs.get("temperature", 0)
    
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # For Docker containers, check if we should use a different URL
        if os.getenv("IN_DOCKER") == "true":
            # If running in Docker, use the Ollama container name
            base_url = os.getenv("OLLAMA_CONTAINER_URL", "http://ollama:11434")
        
        return ChatOllama(
            base_url=base_url,
            model=model_name,
            temperature=temperature,
            **{k: v for k, v in kwargs.items() if k != "temperature"}
        )
    
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            **{k: v for k, v in kwargs.items() if k not in ["temperature", "api_key"]}
        )
    
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            anthropic_api_key=api_key,
            **{k: v for k, v in kwargs.items() if k not in ["temperature", "anthropic_api_key"]}
        )
    
    elif provider == "azure_openai":
        from langchain_openai import AzureChatOpenAI
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", model_name)
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        
        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set")
        
        return AzureChatOpenAI(
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            api_version=api_version,
            api_key=api_key,
            temperature=temperature,
            **{k: v for k, v in kwargs.items() if k not in ["temperature", "api_key"]}
        )
    
    else:
        raise ValueError(f"Unknown provider: {provider}")

def get_embeddings_instance(provider: str, model_name: Optional[str] = None):
    """
    Get embeddings instance based on provider
    
    Args:
        provider: LLM provider
        model_name: Optional model name for embeddings
    
    Returns:
        Embeddings instance
    """
    
    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        if os.getenv("IN_DOCKER") == "true":
            base_url = os.getenv("OLLAMA_CONTAINER_URL", "http://ollama:11434")
        
        # Use a smaller model for embeddings
        embed_model = model_name or "nomic-embed-text"
        
        return OllamaEmbeddings(
            base_url=base_url,
            model=embed_model
        )
    
    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        return OpenAIEmbeddings(
            model=model_name or "text-embedding-3-small",
            api_key=api_key
        )
    
    elif provider == "anthropic":
        # Anthropic doesn't provide embeddings, fall back to OpenAI if available
        if os.getenv("OPENAI_API_KEY"):
            return get_embeddings_instance("openai", model_name)
        else:
            # Use sentence transformers as fallback
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name=model_name or "sentence-transformers/all-MiniLM-L6-v2"
            )
    
    elif provider == "azure_openai":
        from langchain_openai import AzureOpenAIEmbeddings
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "text-embedding-ada-002")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        
        if not api_key or not endpoint:
            raise ValueError("Azure OpenAI credentials not configured")
        
        return AzureOpenAIEmbeddings(
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            api_version=api_version,
            api_key=api_key
        )
    
    else:
        # Default to HuggingFace embeddings
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name=model_name or "sentence-transformers/all-MiniLM-L6-v2"
        )