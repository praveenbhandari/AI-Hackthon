#!/usr/bin/env python
"""
Test script for BC CrewAI FastAPI endpoints
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_research_endpoint():
    """Test the research endpoint"""
    print("\n🔬 Testing Research Endpoint...")
    
    payload = {
        "topic": "AI LLMs",
        "current_year": "2024"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/research", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Execution Time: {result['execution_time']:.2f} seconds")
            print(f"Result Preview: {result['result'][:200]}...")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Research endpoint failed: {e}")
        return False

def test_transit_endpoint():
    """Test the transit endpoint"""
    print("\n🚌 Testing Transit Endpoint...")
    
    payload = {
        "user_request": "I want to go from Salesforce Transit Center to Richmond BART at 08:00 AM",
        "origin": "Salesforce Transit Center",
        "destination": "Richmond BART",
        "time": "08:00",
        "topic": "Bay Area Transit Planning"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/transit", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Execution Time: {result['execution_time']:.2f} seconds")
            print(f"Result Preview: {result['result'][:200]}...")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Transit endpoint failed: {e}")
        return False

def test_full_crew_endpoint():
    """Test the full crew endpoint"""
    print("\n🚀 Testing Full Crew Endpoint...")
    
    payload = {
        "topic": "AI LLMs and Transit Planning",
        "user_request": "Analyze AI LLMs and provide insights about the current state of the technology",
        "origin": "AI Research",
        "destination": "Machine Learning",
        "time": "09:00"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/full", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Execution Time: {result['execution_time']:.2f} seconds")
            print(f"Result Preview: {result['result'][:200]}...")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Full crew endpoint failed: {e}")
        return False

def test_agents_info():
    """Test the agents info endpoint"""
    print("\n🤖 Testing Agents Info Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/agents")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            agents = response.json()['agents']
            print(f"Available Agents: {list(agents.keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Agents info failed: {e}")
        return False

def test_tasks_info():
    """Test the tasks info endpoint"""
    print("\n📋 Testing Tasks Info Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            tasks = response.json()['tasks']
            print(f"Available Tasks: {list(tasks.keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Tasks info failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 BC CrewAI API Test Suite")
    print("=" * 50)
    
    # Check if API is running
    print("🔍 Checking if API is running...")
    if not test_health_check():
        print("❌ API is not running. Please start the API server first:")
        print("   cd bc && python -m bc.api")
        return
    
    # Run tests
    tests = [
        test_research_endpoint,
        test_transit_endpoint,
        test_full_crew_endpoint,
        test_agents_info,
        test_tasks_info
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 