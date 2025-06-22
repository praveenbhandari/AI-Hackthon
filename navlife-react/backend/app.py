from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import asyncio
import subprocess
import json

# Add the parent directory to the path to import the original modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
CORS(app)

# Import the original agent classes
try:
    from food_agent_client import FoodAgent
    from weather_agent_client import WeatherAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent modules not available: {e}")
    AGENTS_AVAILABLE = False

@app.route('/weather', methods=['POST'])
def weather_endpoint():
    """Weather recommendation endpoint"""
    try:
        data = request.get_json()
        location = data.get('location', 'Berkeley, CA')
        
        if AGENTS_AVAILABLE:
            # Call the original weather function
            weather_agent = WeatherAgent()
            result = weather_agent.get_weather_recommendation(location)
            return jsonify(result)
        else:
            # Mock response
            return jsonify({
                "success": True,
                "weather": {
                    "city": location,
                    "country": "US",
                    "temperature": 22,
                    "feels_like": 24,
                    "description": "Partly cloudy",
                    "humidity": 65,
                    "wind_speed": 5
                },
                "recommendation": {
                    "top": "Light sweater or long-sleeve shirt",
                    "bottom": "Jeans or comfortable pants",
                    "outerwear": "Light jacket",
                    "footwear": "Comfortable walking shoes",
                    "accessories": ["Sunglasses", "Hat"]
                },
                "reasoning": "Temperature is moderate with light wind. Comfortable clothing recommended."
            })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/food', methods=['POST'])
def food_endpoint():
    """Food search endpoint"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        location = data.get('location', 'Berkeley, CA')
        
        if AGENTS_AVAILABLE:
            # Call the original food function
            food_agent = FoodAgent(use_typescript=True)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(food_agent.process_query(query, location))
            loop.close()
            return jsonify(result)
        else:
            # Mock response
            return jsonify({
                "success": True,
                "original_query": query,
                "processed_query": query,
                "query_analysis": {"cuisine": "various", "price_range": "moderate"},
                "restaurants": [
                    {
                        "name": "Sample Restaurant",
                        "rating": 4.5,
                        "price_level": 2,
                        "isOpen": True,
                        "address": "123 Main St, Berkeley, CA",
                        "phone": "(555) 123-4567",
                        "website": "https://example.com",
                        "types": ["restaurant", "food"],
                        "photos": []
                    }
                ]
            })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/transit', methods=['POST'])
def transit_endpoint():
    """Transport planning endpoint"""
    try:
        data = request.get_json()
        user_request = data.get('user_request', '')
        origin = data.get('origin', '')
        destination = data.get('destination', '')
        time = data.get('time', '')
        
        # Mock response for now
        return jsonify({
            "success": True,
            "routes": [
                {
                    "type": "Bus",
                    "duration": "25 min",
                    "distance": "2.3 km",
                    "steps": ["Walk to bus stop", "Take bus 51", "Walk to destination"]
                }
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/research', methods=['POST'])
def research_endpoint():
    """Research endpoint"""
    try:
        data = request.get_json()
        topic = data.get('topic', 'AI LLMs')
        current_year = data.get('current_year', '2024')
        
        # Mock response for now
        return jsonify({
            "success": True,
            "research": {
                "topic": topic,
                "year": current_year,
                "summary": f"Research summary for {topic}",
                "sources": ["Source 1", "Source 2"]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/full-crew', methods=['POST'])
def full_crew_endpoint():
    """Full crew endpoint"""
    try:
        data = request.get_json()
        user_request = data.get('user_request', '')
        topic = data.get('topic', 'AI LLMs and Transit Planning')
        origin = data.get('origin', '')
        destination = data.get('destination', '')
        time = data.get('time', '')
        
        # Mock response for now
        return jsonify({
            "success": True,
            "result": {
                "user_request": user_request,
                "topic": topic,
                "origin": origin,
                "destination": destination,
                "time": time,
                "response": "Full crew analysis completed"
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "React backend API is running",
        "agents_available": AGENTS_AVAILABLE
    })

if __name__ == '__main__':
    print("Starting React backend API server...")
    print("Available endpoints:")
    print("  POST /weather - Weather recommendations")
    print("  POST /food - Restaurant search")
    print("  POST /transit - Transport planning")
    print("  POST /research - Research queries")
    print("  POST /full-crew - Full crew operations")
    print("  GET  /health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000) 