#!/usr/bin/env python
"""
Simple test to verify Groq API is working
"""
from dotenv import load_dotenv
load_dotenv()

import os
import requests
import json

def test_groq_api():
    """Test Groq API with a simple completion"""
    print("🔧 Testing Groq API with simple completion...")
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test with Mixtral model
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with 'Groq is working!' if you can see this message."
            }
        ],
        "max_tokens": 50
    }
    
    try:
        print("🚀 Making API call to Groq...")
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Groq API is working! Response: {content}")
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Groq API: {e}")
        return False

if __name__ == "__main__":
    test_groq_api() 