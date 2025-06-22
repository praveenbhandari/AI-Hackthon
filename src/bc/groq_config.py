#!/usr/bin/env python
"""
Groq Configuration Module
Centralized configuration for Groq LLM instances used across the application.
"""

import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables
load_dotenv()

class GroqConfig:
    """Configuration class for Groq LLM instances"""
    
    # Default Groq API key from environment
    DEFAULT_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Available Groq models
    MODELS = {
        'llama3_8b': 'groq/llama3-8b-8192',
        'llama3_70b': 'groq/llama3-70b-8192',
        'mixtral': 'mixtral-8x7b-32768',
        'gemma': 'gemma-7b-it',
        'llama3_1_8b': 'llama-3.1-8b-instant'
    }
    
    @classmethod
    def get_llm(cls, model_name: str = 'llama3_8b', api_key: str = None) -> LLM:
        """
        Get a configured Groq LLM instance
        
        Args:
            model_name: Name of the model to use (from MODELS dict)
            api_key: Optional API key override
            
        Returns:
            Configured LLM instance
        """
        if model_name not in cls.MODELS:
            raise ValueError(f"Unknown model: {model_name}. Available models: {list(cls.MODELS.keys())}")
        
        # Use provided API key or default from environment
        key = api_key or cls.DEFAULT_API_KEY
        if not key:
            raise ValueError("No Groq API key provided. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        return LLM(
            model=cls.MODELS[model_name],
            api_key=key
        )
    
    @classmethod
    def get_fast_llm(cls) -> LLM:
        """Get a fast Groq LLM instance (llama-3.1-8b-instant)"""
        return cls.get_llm('llama3_1_8b')
    
    @classmethod
    def get_balanced_llm(cls) -> LLM:
        """Get a balanced Groq LLM instance (llama3-8b)"""
        return cls.get_llm('llama3_8b')
    
    @classmethod
    def get_powerful_llm(cls) -> LLM:
        """Get a powerful Groq LLM instance (llama3-70b)"""
        return cls.get_llm('llama3_70b')
    
    @classmethod
    def get_mixtral_llm(cls) -> LLM:
        """Get a Mixtral Groq LLM instance"""
        return cls.get_llm('mixtral')
    
    @classmethod
    def get_gemma_llm(cls) -> LLM:
        """Get a Gemma Groq LLM instance"""
        return cls.get_llm('gemma')

# Pre-configured LLM instances for easy import
groq_fast = GroqConfig.get_fast_llm()
groq_balanced = GroqConfig.get_balanced_llm()
groq_powerful = GroqConfig.get_powerful_llm()
groq_mixtral = GroqConfig.get_mixtral_llm()
groq_gemma = GroqConfig.get_gemma_llm()

# Default LLM for backward compatibility
groq_llm = groq_balanced 