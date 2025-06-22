import gradio as gr
import requests
import json
import os
import asyncio
from typing import Dict, List, Any, Optional

# Import the agent classes
from food_agent_client import FoodAgent
from weather_agent_client import WeatherAgent

# API Base URL
API_BASE_URL = "http://localhost:9876"

# Weather Feature Functions
def get_weather_recommendation(location: str) -> Dict[str, Any]:
    """Get weather-based clothing recommendations for a location by directly calling the Node.js script."""
    try:
        # Call the Node.js script directly to avoid any potential caching issues
        import subprocess
        import json
        
        # Make location more specific to ensure we get the correct data
        # If the location is Berkeley, make it Berkeley,CA,US to be more specific
        if location.lower() == "berkeley":
            location = "Berkeley,CA,US"
        elif "berkeley" in location.lower() and "," not in location:
            location = location + ",US"
        
        print(f"Getting weather for: {location}")
        
        # Run the JavaScript script with Node.js
        cmd = ["node", "agentic-weather.js", location]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse the output to extract the JSON result
        output = result.stdout
        
        # Find the JSON part in the output (after "Results:")
        results_marker = "Results:\n"
        results_pos = output.find(results_marker)
        
        if results_pos == -1:
            raise ValueError("Could not find 'Results:' marker in output")
                
        json_str = output[results_pos + len(results_marker):].strip()
        data = json.loads(json_str)
        
        return data
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f"Error running JavaScript: {e.stderr}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing weather request: {str(e)}"
        }

def format_weather_output(result: Dict[str, Any]) -> str:
    """Format weather recommendation results as HTML."""
    if not result.get("success", False):
        return f"<div class='error'>{result.get('message', 'Unknown error')}</div>"
    
    weather = result.get("weather", {})
    recommendation = result.get("recommendation", {})
    reasoning = result.get("reasoning", "")
    
    html = f"""
    <div style='display: flex; flex-wrap: wrap; gap: 20px;'>
        <div style='flex: 1; min-width: 300px;'>
            <h3>Current Weather in {weather.get('city', '')}, {weather.get('country', '')}</h3>
            <p><strong>Temperature:</strong> {weather.get('temperature', '')}°C (feels like {weather.get('feels_like', '')}°C)</p>
            <p><strong>Conditions:</strong> {weather.get('description', '')}</p>
            <p><strong>Humidity:</strong> {weather.get('humidity', '')}%</p>
            <p><strong>Wind Speed:</strong> {weather.get('wind_speed', '')} m/s</p>
        </div>
        <div style='flex: 1; min-width: 300px;'>
            <h3>Clothing Recommendations</h3>
            <p><strong>Top:</strong> {recommendation.get('top', '')}</p>
            <p><strong>Bottom:</strong> {recommendation.get('bottom', '')}</p>
            <p><strong>Outerwear:</strong> {recommendation.get('outerwear', '')}</p>
            <p><strong>Footwear:</strong> {recommendation.get('footwear', '')}</p>
            <p><strong>Accessories:</strong> {', '.join(recommendation.get('accessories', []))}</p>
        </div>
    </div>
    <div style='margin-top: 20px;'>
        <h3>Reasoning</h3>
        <p>{reasoning}</p>
    </div>
    """
    return html

# Food Feature Functions
def search_restaurants(query: str, location: str = "Berkeley, CA") -> Dict[str, Any]:
    """Search for restaurants based on a natural language query using the FoodAgent directly."""
    try:
        # Initialize the FoodAgent
        food_agent = FoodAgent(use_typescript=True)
        
        # Process the query asynchronously but run it in the synchronous context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(food_agent.process_query(query, location))
        loop.close()
        
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing food query: {str(e)}"
        }

def format_restaurant_output(result: Dict[str, Any]) -> str:
    """Format restaurant search results as HTML."""
    if not result.get("success", False):
        return f"<div class='error'>{result.get('message', 'Unknown error')}</div>"
    
    # Extract query information from the result structure
    original_query = result.get("original_query", "")
    processed_query = result.get("processed_query", "")
    query_analysis = result.get("query_analysis", {})
    restaurants = result.get("restaurants", [])
    
    html = f"""
    <div>
        <p><strong>Query:</strong> "{original_query}"</p>
        <p><strong>Parsed as:</strong> {json.dumps(query_analysis)}</p>
        <h3>Restaurants ({len(restaurants)})</h3>
    </div>
    """
    
    for restaurant in restaurants:
        # Generate star rating
        full_stars = "★" * int(restaurant.get("rating", 0))
        half_star = "½" if restaurant.get("rating", 0) % 1 >= 0.5 else ""
        empty_stars = "☆" * (5 - int(restaurant.get("rating", 0)) - (1 if half_star else 0))
        stars = f"{full_stars}{half_star}{empty_stars} {restaurant.get('rating', 0)}"
        
        # Price level
        price = "$" * restaurant.get("price_level", 0)
        
        # Open/closed status
        status_color = "green" if restaurant.get("isOpen", False) else "red"
        status_text = "Open" if restaurant.get("isOpen", False) else "Closed"
        
        html += f"""
        <div style='border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                <h4 style='margin: 0;'>{restaurant.get('name', '')}</h4>
                <span style='color: {status_color};'>{status_text}</span>
            </div>
            <div style='color: gold;'>{stars}</div>
            <div style='display: flex; gap: 10px; color: #666;'>
                <div>{price}</div>
                <div>• {restaurant.get('distance', '')} miles</div>
                {f"<div>• {', '.join(restaurant.get('dietary', []))}</div>" if restaurant.get('dietary', []) else ""}
            </div>
            <div>{', '.join(restaurant.get('categories', []))}</div>
        </div>
        """
    
    return html

# Fallback functions for when API is not available
def weather_fallback(location: str) -> str:
    """Fallback function when Weather Agent is not available."""
    return """
    <div style='padding: 20px; background-color: #f8f9fa; border-left: 4px solid #ffc107;'>
        <h3>Weather Agent Not Available</h3>
        <p>The Weather Agent seems to be unavailable. Please make sure:</p>
        <ol>
            <li>You have installed the required dependencies: <code>npm install</code></li>
            <li>You have set up the OpenWeatherMap API key in your .env file</li>
            <li>You have set up the Gemini API key in your .env file</li>
        </ol>
        <p>Sample weather recommendation would appear here.</p>
    </div>
    """

def food_fallback(query: str, location: str) -> str:
    """Fallback function when Food Agent is not available."""
    return """
    <div style='padding: 20px; background-color: #f8f9fa; border-left: 4px solid #ffc107;'>
        <h3>Food Agent Not Available</h3>
        <p>The Food Agent seems to be unavailable. Please make sure:</p>
        <ol>
            <li>You have installed the required dependencies: <code>npm install</code></li>
            <li>The TypeScript agent is properly configured</li>
            <li>You have set up the Google Places API key in your .env file</li>
        </ol>
        <p>Sample restaurant recommendations would appear here.</p>
    </div>
    """

# Gradio Interface Functions
def weather_interface(location: str) -> str:
    """Interface function for weather tab."""
    try:
        result = get_weather_recommendation(location)
        return format_weather_output(result)
    except Exception as e:
        return weather_fallback(location)

def food_interface(query: str, location: str) -> str:
    """Interface function for food tab."""
    try:
        result = search_restaurants(query, location)
        return format_restaurant_output(result)
    except Exception as e:
        return food_fallback(query, location)

# Create Gradio App
with gr.Blocks(css="""
    .gradio-container {max-width: 900px !important}
    .error {color: #ff4757; padding: 10px; background-color: #ffebee; border-radius: 4px;}
""") as app:
    gr.Markdown("# NavLife App")
    
    with gr.Tabs():
        with gr.TabItem("Weather"):
            gr.Markdown("## Weather-Based Clothing Recommendations")
            with gr.Row():
                location_input = gr.Textbox(
                    label="Location", 
                    placeholder="Enter location (e.g., Berkeley,CA,US)",
                    value="Berkeley,CA,US"
                )
            
            with gr.Row():
                weather_button = gr.Button("Get Recommendations", variant="primary")
            
            weather_output = gr.HTML(
                weather_fallback(""),
                label="Recommendations"
            )
            
            weather_button.click(
                fn=weather_interface,
                inputs=location_input,
                outputs=weather_output
            )
        
        with gr.TabItem("Food"):
            gr.Markdown("## Restaurant Discovery")
            with gr.Row():
                food_query = gr.Textbox(
                    label="What are you craving?", 
                    placeholder="e.g., spicy Indian food with outdoor seating"
                )
                food_location = gr.Textbox(
                    label="Location",
                    value="Berkeley, CA",
                    placeholder="e.g., Berkeley, CA"
                )
            
            food_button = gr.Button("Search Restaurants", variant="primary")
            
            food_output = gr.HTML(
                food_fallback("", ""),
                label="Restaurant Recommendations"
            )
            
            food_button.click(
                fn=food_interface,
                inputs=[food_query, food_location],
                outputs=food_output
            )
        
        with gr.TabItem("Transport"):
            gr.Markdown("## Transport Feature")
            gr.Markdown("This feature is coming soon!")
        
        with gr.TabItem("Safety"):
            gr.Markdown("## Safety Feature")
            gr.Markdown("This feature is coming soon!")

# Launch the app
if __name__ == "__main__":
    app.launch(share=False)
