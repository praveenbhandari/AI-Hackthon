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

def test_safety_routes_endpoint():
    """Test the safety routes endpoint"""
    print("\n🛡️ Testing Safety Routes Endpoint...")
    
    payload = {
        "start_lat": 37.7694,
        "start_lng": -122.4862,
        "end_lat": 37.8087,
        "end_lng": -122.4098,
        "safety_weight": 0.7,
        "max_distance_factor": 2.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/safety_routes", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Total Routes: {result['total_routes']}")
            print(f"Execution Time: {result['execution_time']:.2f} seconds")
            print(f"Routing Method: {result['routing_method']}")
            
            if result.get('best_route'):
                best_route = result['best_route']
                print(f"Best Route Type: {best_route.get('route_type')}")
                print(f"Best Route Safety Score: {best_route.get('avg_safety_score')}")
                print(f"Best Route Safety Grade: {best_route.get('safety_grade')}")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Safety routes endpoint failed: {e}")
        return False

def test_safety_info_endpoint():
    """Test the safety info endpoint"""
    print("\n🔍 Testing Safety Info Endpoint...")
    
    payload = {
        "lat": 37.7694,
        "lng": -122.4862,
        "radius_meters": 500
    }
    
    try:
        response = requests.post(f"{BASE_URL}/safety_info", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Safety Score: {result['safety_score']}")
            print(f"Safety Grade: {result['safety_grade']}")
            print(f"Nearby Incidents: {result['nearby_incidents']}")
            print(f"Execution Time: {result['execution_time']:.2f} seconds")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Safety info endpoint failed: {e}")
        return False

def test_incident_data_endpoint():
    """Test the incident data endpoint"""
    print("\n📊 Testing Incident Data Endpoint...")
    
    payload = {
        "limit": 1000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/incident_data", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Total Incidents: {result['total_incidents']}")
            print(f"Limit: {result['limit']}")
            print(f"Execution Time: {result['execution_time']:.2f} seconds")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Incident data endpoint failed: {e}")
        return False

def test_safety_analysis_endpoint():
    """Test the safety analysis endpoint"""
    print("\n📈 Testing Safety Analysis Endpoint...")
    
    payload = {
        "safety_analysis_request": "Analyze safety patterns in San Francisco",
        "topic": "Safety Analysis"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/safety_analysis", json=payload)
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
        print(f"❌ Safety analysis endpoint failed: {e}")
        return False

def test_route_planning_endpoint():
    """Test the route planning endpoint"""
    print("\n🗺️ Testing Route Planning Endpoint...")
    
    payload = {
        "route_planning_request": "Find safe route from Golden Gate Park to Fisherman's Wharf",
        "user_preferences": "Safety-focused, walking preferred, avoid high-crime areas",
        "safety_requirements": "Avoid high-crime areas, well-lit routes, populated areas",
        "start_lat": 37.7694,
        "start_lng": -122.4862,
        "end_lat": 37.8087,
        "end_lng": -122.4098,
        "safety_weight": 0.7
    }
    
    try:
        response = requests.post(f"{BASE_URL}/route_planning", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Execution Time: {result['execution_time']:.2f} seconds")
            
            if result.get('recommendations'):
                print("Recommendations:")
                for rec in result['recommendations']:
                    print(f"  - {rec}")
        else:
            print(f"Error: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Route planning endpoint failed: {e}")
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

def test_tools_info():
    """Test the tools info endpoint"""
    print("\n🔧 Testing Tools Info Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/tools")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            tools = response.json()['tools']
            print(f"Available Tools: {list(tools.keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Tools info failed: {e}")
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
        test_safety_routes_endpoint,
        test_safety_info_endpoint,
        test_incident_data_endpoint,
        test_safety_analysis_endpoint,
        test_route_planning_endpoint,
        test_full_crew_endpoint,
        test_agents_info,
        test_tasks_info,
        test_tools_info
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