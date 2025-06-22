#!/usr/bin/env python
"""
Test script to verify CORS configuration is working
"""
import requests
import json

def test_cors_health_check():
    """Test the health check endpoint with CORS headers"""
    print("🧪 Testing CORS Configuration...")
    
    # Test the main API on port 8000
    try:
        # Make a request to the health endpoint
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health check status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        
        # Check if CORS headers are present
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        print("\n🔍 Checking CORS headers...")
        for header in cors_headers:
            if header in response.headers:
                print(f"✅ {header}: {response.headers[header]}")
            else:
                print(f"❌ {header}: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def test_cors_preflight():
    """Test CORS preflight request"""
    print("\n🧪 Testing CORS Preflight Request...")
    
    try:
        # Make an OPTIONS request (preflight)
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options("http://localhost:8000/health", headers=headers)
        print(f"✅ Preflight status: {response.status_code}")
        
        # Check CORS headers in preflight response
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        for header in cors_headers:
            if header in response.headers:
                print(f"✅ {header}: {response.headers[header]}")
            else:
                print(f"❌ {header}: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Preflight test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting CORS Configuration Test")
    print("=" * 50)
    
    # Test basic health check
    health_success = test_cors_health_check()
    
    # Test preflight request
    preflight_success = test_cors_preflight()
    
    print("\n" + "=" * 50)
    if health_success and preflight_success:
        print("🎉 CORS configuration appears to be working correctly!")
        print("✅ Your frontend should now be able to make requests to the API")
    else:
        print("❌ CORS configuration may have issues")
        print("🔧 Make sure the API server is running on port 8000") 