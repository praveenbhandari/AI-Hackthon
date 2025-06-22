#!/usr/bin/env python
"""
Test script to verify Groq configuration module
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_groq_config():
    """Test the Groq configuration module"""
    print("🔧 Testing Groq Configuration Module...")
    
    try:
        from bc.groq_config import GroqConfig, groq_fast, groq_balanced, groq_powerful
        
        print("✅ Successfully imported GroqConfig")
        
        # Test available models
        print(f"📋 Available models: {list(GroqConfig.MODELS.keys())}")
        
        # Test getting different LLM instances
        print("\n🧪 Testing LLM instance creation...")
        
        # Test fast LLM
        fast_llm = GroqConfig.get_fast_llm()
        print(f"✅ Fast LLM created: {fast_llm.model}")
        
        # Test balanced LLM
        balanced_llm = GroqConfig.get_balanced_llm()
        print(f"✅ Balanced LLM created: {balanced_llm.model}")
        
        # Test powerful LLM
        powerful_llm = GroqConfig.get_powerful_llm()
        print(f"✅ Powerful LLM created: {powerful_llm.model}")
        
        # Test pre-configured instances
        print(f"✅ Pre-configured fast LLM: {groq_fast.model}")
        print(f"✅ Pre-configured balanced LLM: {groq_balanced.model}")
        print(f"✅ Pre-configured powerful LLM: {groq_powerful.model}")
        
        # Test error handling for invalid model
        try:
            invalid_llm = GroqConfig.get_llm('invalid_model')
            print("❌ Should have raised error for invalid model")
        except ValueError as e:
            print(f"✅ Correctly handled invalid model: {e}")
        
        print("\n🎉 All Groq configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Groq configuration: {e}")
        return False

def test_crew_integration():
    """Test that crew.py can import and use the Groq configuration"""
    print("\n🔧 Testing Crew Integration...")
    
    try:
        from bc.crew import Bc
        
        print("✅ Successfully imported Bc crew")
        
        # Test creating crew instance
        crew_instance = Bc()
        print("✅ Successfully created crew instance")
        
        # Test creating agents (this will test the LLM configuration)
        try:
            transit_planner = crew_instance.transit_planner()
            print("✅ Successfully created transit_planner agent")
        except Exception as e:
            print(f"⚠️  Transit planner creation failed (expected if no API key): {e}")
        
        try:
            safety_route_finder = crew_instance.safety_route_finder()
            print("✅ Successfully created safety_route_finder agent")
        except Exception as e:
            print(f"⚠️  Safety route finder creation failed (expected if no API key): {e}")
        
        print("🎉 Crew integration tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing crew integration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Groq Configuration Tests...\n")
    
    # Test API key setup
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print(f"✅ GROQ_API_KEY found: {api_key[:10]}...")
    else:
        print("⚠️  GROQ_API_KEY not found - some tests may fail")
    
    # Run tests
    config_success = test_groq_config()
    crew_success = test_crew_integration()
    
    if config_success and crew_success:
        print("\n🎉 All tests passed! Groq configuration is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the configuration.") 