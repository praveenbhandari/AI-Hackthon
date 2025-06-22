#!/usr/bin/env python
"""
Test script to verify Groq API key setup
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_groq_api_key():
    """Test if Groq API key is properly set"""
    print("🔧 Testing Groq API Key Setup...")
    
    # Check if API key is set
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("❌ GROQ_API_KEY environment variable is not set")
        print("Please set your Groq API key using one of these methods:")
        print("1. Create a .env file with: GROQ_API_KEY=your-key-here")
        print("2. Set environment variable: export GROQ_API_KEY='your-key-here'")
        print("3. Add to ~/.zshrc: export GROQ_API_KEY='your-key-here'")
        return False
    
    if api_key == "your-groq-api-key-here" or "your-actual-groq-api-key-here" in api_key:
        print("❌ Please replace the placeholder with your actual Groq API key")
        return False
    
    print(f"✅ GROQ_API_KEY is set: {api_key[:10]}...")
    
    # Test with a simple API call
    try:
        from bc.crew import Bc
        crew_instance = Bc()
        
        # Test safety route finder agent
        agent = crew_instance.safety_route_finder()
        print("✅ Safety route finder agent created successfully")
        
        # Test with simple inputs
        inputs = {
            'start_lat': 37.7694,
            'start_lng': -122.4862,
            'end_lat': 37.8087,
            'end_lng': -122.4098,
            'safety_weight': 0.7
        }
        
        print("✅ Groq API key is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Groq API: {e}")
        return False

if __name__ == "__main__":
    test_groq_api_key() 