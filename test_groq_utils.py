#!/usr/bin/env python
"""
Test script for Groq utilities module
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_groq_utils():
    """Test the groq_utils module functions"""
    print("🔧 Testing Groq Utilities Module...")
    
    try:
        from bc.groq_utils import (
            get_llm_for_task,
            get_agent_llm_config,
            validate_groq_setup,
            print_groq_status
        )
        
        print("✅ Successfully imported groq_utils functions")
        
        # Test get_llm_for_task
        print("\n🧪 Testing get_llm_for_task...")
        
        # Test different task types
        task_types = ['transit', 'safety', 'analysis', 'research', 'planning']
        complexities = ['fast', 'balanced', 'powerful']
        
        for task_type in task_types:
            for complexity in complexities:
                try:
                    llm = get_llm_for_task(task_type, complexity)
                    print(f"✅ {task_type} ({complexity}): {llm.model}")
                except Exception as e:
                    print(f"❌ {task_type} ({complexity}): {e}")
        
        # Test get_agent_llm_config
        print("\n🧪 Testing get_agent_llm_config...")
        
        agent_names = [
            'transit_planner', 'transit_analyst', 'route_optimizer',
            'safety_route_finder', 'safety_analyst', 'route_planner',
            'researcher', 'reporting_analyst', 'claude_agent'
        ]
        
        for agent_name in agent_names:
            try:
                config = get_agent_llm_config(agent_name)
                print(f"✅ {agent_name}: {config['llm'].model} - {config['reasoning']}")
            except Exception as e:
                print(f"❌ {agent_name}: {e}")
        
        # Test unknown agent (should use default)
        try:
            config = get_agent_llm_config('unknown_agent')
            print(f"✅ unknown_agent (default): {config['llm'].model} - {config['reasoning']}")
        except Exception as e:
            print(f"❌ unknown_agent: {e}")
        
        # Test validate_groq_setup
        print("\n🧪 Testing validate_groq_setup...")
        
        status = validate_groq_setup()
        print(f"✅ API Key Set: {status['api_key_set']}")
        print(f"✅ API Key Valid: {status['api_key_valid']}")
        print(f"✅ Available Models: {status['models_available']}")
        
        if status['errors']:
            print("⚠️  Errors found:")
            for error in status['errors']:
                print(f"   - {error}")
        else:
            print("✅ No errors found")
        
        # Test print_groq_status
        print("\n🧪 Testing print_groq_status...")
        print_groq_status()
        
        print("\n🎉 All Groq utilities tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Groq utilities: {e}")
        return False

def test_error_handling():
    """Test error handling in groq_utils"""
    print("\n🔧 Testing Error Handling...")
    
    try:
        from bc.groq_utils import get_llm_for_task, get_agent_llm_config
        
        # Test invalid task type
        try:
            llm = get_llm_for_task('invalid_task', 'fast')
            print("❌ Should have raised error for invalid task type")
        except ValueError as e:
            print(f"✅ Correctly handled invalid task type: {e}")
        
        # Test invalid complexity
        try:
            llm = get_llm_for_task('transit', 'invalid_complexity')
            print("❌ Should have raised error for invalid complexity")
        except ValueError as e:
            print(f"✅ Correctly handled invalid complexity: {e}")
        
        print("🎉 Error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing error handling: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Groq Utilities Tests...\n")
    
    # Test API key setup
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print(f"✅ GROQ_API_KEY found: {api_key[:10]}...")
    else:
        print("⚠️  GROQ_API_KEY not found - some tests may fail")
    
    # Run tests
    utils_success = test_groq_utils()
    error_success = test_error_handling()
    
    if utils_success and error_success:
        print("\n🎉 All Groq utilities tests passed!")
    else:
        print("\n❌ Some tests failed. Please check the configuration.") 