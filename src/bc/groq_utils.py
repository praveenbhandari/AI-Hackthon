#!/usr/bin/env python
"""
Groq Utilities Module
Helper functions for working with Groq LLMs in different contexts.
"""

from typing import Dict, Any, Optional
from bc.groq_config import GroqConfig

def get_llm_for_task(task_type: str, complexity: str = 'balanced') -> Any:
    """
    Get the appropriate Groq LLM for a specific task type and complexity
    
    Args:
        task_type: Type of task ('transit', 'safety', 'analysis', 'research', 'planning')
        complexity: Task complexity ('fast', 'balanced', 'powerful')
        
    Returns:
        Configured LLM instance
    """
    # Task-specific LLM recommendations
    task_llm_map = {
        'transit': {
            'fast': 'llama3_1_8b',
            'balanced': 'llama3_8b',
            'powerful': 'llama3_70b'
        },
        'safety': {
            'fast': 'llama3_1_8b',
            'balanced': 'llama3_8b',
            'powerful': 'llama3_70b'
        },
        'analysis': {
            'fast': 'llama3_8b',
            'balanced': 'llama3_70b',
            'powerful': 'mixtral'
        },
        'research': {
            'fast': 'llama3_8b',
            'balanced': 'llama3_70b',
            'powerful': 'mixtral'
        },
        'planning': {
            'fast': 'llama3_1_8b',
            'balanced': 'llama3_8b',
            'powerful': 'llama3_70b'
        }
    }
    
    if task_type not in task_llm_map:
        raise ValueError(f"Unknown task type: {task_type}")
    
    if complexity not in task_llm_map[task_type]:
        raise ValueError(f"Unknown complexity level: {complexity}")
    
    model_name = task_llm_map[task_type][complexity]
    return GroqConfig.get_llm(model_name)

def get_agent_llm_config(agent_name: str) -> Dict[str, Any]:
    """
    Get LLM configuration for a specific agent
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Dictionary with LLM configuration
    """
    agent_configs = {
        'transit_planner': {
            'llm': GroqConfig.get_fast_llm(),
            'reasoning': 'Fast response for real-time transit planning'
        },
        'transit_analyst': {
            'llm': GroqConfig.get_balanced_llm(),
            'reasoning': 'Balanced performance for detailed analysis'
        },
        'route_optimizer': {
            'llm': GroqConfig.get_balanced_llm(),
            'reasoning': 'Balanced performance for optimization tasks'
        },
        'safety_route_finder': {
            'llm': GroqConfig.get_fast_llm(),
            'reasoning': 'Fast response for safety-critical routing'
        },
        'safety_analyst': {
            'llm': GroqConfig.get_balanced_llm(),
            'reasoning': 'Balanced performance for safety analysis'
        },
        'route_planner': {
            'llm': GroqConfig.get_balanced_llm(),
            'reasoning': 'Balanced performance for comprehensive planning'
        },
        'researcher': {
            'llm': GroqConfig.get_powerful_llm(),
            'reasoning': 'Powerful model for research tasks'
        },
        'reporting_analyst': {
            'llm': GroqConfig.get_balanced_llm(),
            'reasoning': 'Balanced performance for report generation'
        },
        'claude_agent': {
            'llm': GroqConfig.get_powerful_llm(),
            'reasoning': 'Powerful model for Claude-style analysis'
        }
    }
    
    if agent_name not in agent_configs:
        # Default to balanced LLM for unknown agents
        return {
            'llm': GroqConfig.get_balanced_llm(),
            'reasoning': 'Default balanced configuration'
        }
    
    return agent_configs[agent_name]

def validate_groq_setup() -> Dict[str, Any]:
    """
    Validate the Groq setup and return status information
    
    Returns:
        Dictionary with validation results
    """
    status = {
        'api_key_set': False,
        'api_key_valid': False,
        'models_available': [],
        'errors': []
    }
    
    try:
        # Check if API key is set
        api_key = GroqConfig.DEFAULT_API_KEY
        if api_key:
            status['api_key_set'] = True
            
            # Test API key with a simple model
            try:
                test_llm = GroqConfig.get_fast_llm()
                status['api_key_valid'] = True
                status['models_available'].append('llama3_1_8b')
            except Exception as e:
                status['errors'].append(f"API key validation failed: {e}")
        
        # Test all available models
        for model_name in GroqConfig.MODELS.keys():
            try:
                test_llm = GroqConfig.get_llm(model_name)
                if model_name not in status['models_available']:
                    status['models_available'].append(model_name)
            except Exception as e:
                status['errors'].append(f"Model {model_name} failed: {e}")
                
    except Exception as e:
        status['errors'].append(f"Setup validation failed: {e}")
    
    return status

def print_groq_status():
    """Print a formatted status of the Groq setup"""
    status = validate_groq_setup()
    
    print("🔧 Groq Setup Status:")
    print(f"   API Key Set: {'✅' if status['api_key_set'] else '❌'}")
    print(f"   API Key Valid: {'✅' if status['api_key_valid'] else '❌'}")
    print(f"   Available Models: {', '.join(status['models_available'])}")
    
    if status['errors']:
        print("   Errors:")
        for error in status['errors']:
            print(f"     - {error}")
    else:
        print("   ✅ No errors found") 