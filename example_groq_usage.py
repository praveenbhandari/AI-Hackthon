#!/usr/bin/env python
"""
Example script demonstrating how to use the Groq configuration system
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def example_basic_usage():
    """Example of basic Groq configuration usage"""
    print("🚀 Example: Basic Groq Configuration Usage")
    print("=" * 50)
    
    try:
        from bc.groq_config import GroqConfig, groq_fast, groq_balanced, groq_powerful
        
        # Method 1: Use pre-configured instances
        print("1. Using pre-configured instances:")
        print(f"   Fast LLM: {groq_fast.model}")
        print(f"   Balanced LLM: {groq_balanced.model}")
        print(f"   Powerful LLM: {groq_powerful.model}")
        
        # Method 2: Get specific model
        print("\n2. Getting specific models:")
        llama3_8b = GroqConfig.get_llm('llama3_8b')
        print(f"   llama3_8b: {llama3_8b.model}")
        
        # Method 3: Get by performance level
        print("\n3. Getting by performance level:")
        fast_llm = GroqConfig.get_fast_llm()
        balanced_llm = GroqConfig.get_balanced_llm()
        powerful_llm = GroqConfig.get_powerful_llm()
        print(f"   Fast: {fast_llm.model}")
        print(f"   Balanced: {balanced_llm.model}")
        print(f"   Powerful: {powerful_llm.model}")
        
        print("\n✅ Basic usage example completed!")
        
    except Exception as e:
        print(f"❌ Error in basic usage example: {e}")

def example_task_specific_usage():
    """Example of task-specific LLM selection"""
    print("\n🚀 Example: Task-Specific LLM Selection")
    print("=" * 50)
    
    try:
        from bc.groq_utils import get_llm_for_task
        
        # Example tasks
        tasks = [
            ('transit', 'fast', 'Real-time transit planning'),
            ('analysis', 'powerful', 'Complex data analysis'),
            ('safety', 'balanced', 'Safety route planning'),
            ('research', 'powerful', 'Deep research tasks')
        ]
        
        for task_type, complexity, description in tasks:
            llm = get_llm_for_task(task_type, complexity)
            print(f"Task: {task_type} ({complexity})")
            print(f"   Description: {description}")
            print(f"   Selected LLM: {llm.model}")
            print()
        
        print("✅ Task-specific usage example completed!")
        
    except Exception as e:
        print(f"❌ Error in task-specific usage example: {e}")

def example_agent_configuration():
    """Example of agent-specific LLM configuration"""
    print("\n🚀 Example: Agent-Specific Configuration")
    print("=" * 50)
    
    try:
        from bc.groq_utils import get_agent_llm_config
        
        # Example agents
        agents = [
            'transit_planner',
            'safety_route_finder', 
            'researcher',
            'claude_agent'
        ]
        
        for agent_name in agents:
            config = get_agent_llm_config(agent_name)
            print(f"Agent: {agent_name}")
            print(f"   LLM: {config['llm'].model}")
            print(f"   Reasoning: {config['reasoning']}")
            print()
        
        print("✅ Agent configuration example completed!")
        
    except Exception as e:
        print(f"❌ Error in agent configuration example: {e}")

def example_validation_and_status():
    """Example of validation and status checking"""
    print("\n🚀 Example: Validation and Status")
    print("=" * 50)
    
    try:
        from bc.groq_utils import validate_groq_setup, print_groq_status
        
        # Get detailed status
        status = validate_groq_setup()
        print("Detailed Status:")
        print(f"   API Key Set: {status['api_key_set']}")
        print(f"   API Key Valid: {status['api_key_valid']}")
        print(f"   Available Models: {', '.join(status['models_available'])}")
        
        if status['errors']:
            print("   Errors:")
            for error in status['errors']:
                print(f"     - {error}")
        
        print("\nFormatted Status:")
        print_groq_status()
        
        print("\n✅ Validation example completed!")
        
    except Exception as e:
        print(f"❌ Error in validation example: {e}")

def example_crew_integration():
    """Example of how the configuration integrates with CrewAI"""
    print("\n🚀 Example: CrewAI Integration")
    print("=" * 50)
    
    try:
        from bc.crew import Bc
        
        # Create crew instance
        crew_instance = Bc()
        print("✅ Created Bc crew instance")
        
        # Show how different agents use different LLMs
        agents_to_test = [
            ('transit_planner', 'Fast LLM for real-time planning'),
            ('safety_route_finder', 'Fast LLM for safety-critical routing'),
            ('researcher', 'Powerful LLM for research tasks')
        ]
        
        for agent_name, description in agents_to_test:
            try:
                agent = getattr(crew_instance, agent_name)()
                print(f"✅ {agent_name}: {description}")
                print(f"   Using LLM: {agent.llm.model}")
            except Exception as e:
                print(f"⚠️  {agent_name}: {e}")
        
        print("\n✅ CrewAI integration example completed!")
        
    except Exception as e:
        print(f"❌ Error in CrewAI integration example: {e}")

def example_error_handling():
    """Example of error handling"""
    print("\n🚀 Example: Error Handling")
    print("=" * 50)
    
    try:
        from bc.groq_config import GroqConfig
        from bc.groq_utils import get_llm_for_task
        
        # Test invalid model
        try:
            invalid_llm = GroqConfig.get_llm('invalid_model')
            print("❌ Should have raised error for invalid model")
        except ValueError as e:
            print(f"✅ Correctly handled invalid model: {e}")
        
        # Test invalid task type
        try:
            invalid_task = get_llm_for_task('invalid_task', 'fast')
            print("❌ Should have raised error for invalid task")
        except ValueError as e:
            print(f"✅ Correctly handled invalid task: {e}")
        
        # Test invalid complexity
        try:
            invalid_complexity = get_llm_for_task('transit', 'invalid_complexity')
            print("❌ Should have raised error for invalid complexity")
        except ValueError as e:
            print(f"✅ Correctly handled invalid complexity: {e}")
        
        print("\n✅ Error handling example completed!")
        
    except Exception as e:
        print(f"❌ Error in error handling example: {e}")

if __name__ == "__main__":
    print("🎯 Groq Configuration System Examples")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print(f"✅ GROQ_API_KEY found: {api_key[:10]}...")
    else:
        print("⚠️  GROQ_API_KEY not found - some examples may fail")
    
    print()
    
    # Run examples
    example_basic_usage()
    example_task_specific_usage()
    example_agent_configuration()
    example_validation_and_status()
    example_crew_integration()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("🎉 All examples completed!")
    print("\nFor more information, see GROQ_CONFIG_README.md") 