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

# --- Transport Feature Functions ---
TRANSPORT_API_URL = os.getenv("TRANSPORT_API_URL", "http://localhost:8001/agents/transit_planner_json")

def get_transport_routes(user_request: str, origin: str, destination: str, time: str) -> dict:
    payload = {
        "user_request": user_request,
        "origin": origin,
        "destination": destination,
        "time": time
    }
    try:
        resp = requests.post(TRANSPORT_API_URL, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": f"Transport API error: {str(e)}"}

def format_transport_output(result: dict) -> str:
    if not result.get("success", False):
        return f"<div class='error'>{result.get('message', 'Unknown error')}</div>"
    data = result.get("data") or result
    routes = data.get("transit_routes", [])
    summary = data.get("summary", {})
    html = "<h3>Transit Routes</h3>"
    for route in routes:
        html += f"<div style='border:1px solid #ccc; border-radius:8px; padding:10px; margin-bottom:10px;'>"
        html += f"<b>Route ID:</b> {route.get('route_id')}<br>"
        html += f"<b>Type:</b> {route.get('route_type', '')}<br>"
        html += f"<b>Departure:</b> {route.get('departure_time')} | <b>Arrival:</b> {route.get('arrival_time')}<br>"
        html += f"<b>Time Taken:</b> {route.get('time_taken')} | <b>Cost:</b> ${route.get('cost')}<br>"
        html += f"<b>Stops:</b><ul>"
        for stop in route.get('stops', []):
            html += f"<li>{stop.get('stop_number')}: {stop.get('stop_name')} ({stop.get('arrival_time')} - {stop.get('departure_time')})</li>"
        html += "</ul>"
        html += f"<b>Total Stops:</b> {route.get('total_stops', '')}"
        html += "</div>"
    if summary:
        html += f"<h4>Summary</h4><pre>{json.dumps(summary, indent=2)}</pre>"
    return html

def transport_interface(user_request: str, origin: str, destination: str, time: str) -> str:
    result = get_transport_routes(user_request, origin, destination, time)
    return format_transport_output(result)

# --- Safety Feature Functions ---
SAFETY_API_URL = os.getenv("SAFETY_API_URL", "http://localhost:8001/agents/safety_router")
SAFETY_ROUTE_API_URL = os.getenv("SAFETY_ROUTE_API_URL", "http://localhost:8001/safety/route")

def get_safety_route(user_request: str, safety_weight: float = 0.7) -> dict:
    payload = {
        "user_request": user_request,
        "origin": str(safety_weight)  # Used for safety_weight in backend
    }
    try:
        resp = requests.post(SAFETY_API_URL, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": f"Safety API error: {str(e)}"}

def get_safety_route_with_coords(start_lat: float, start_lng: float, end_lat: float, end_lng: float, safety_weight: float = 0.7) -> dict:
    """Get safety route using direct coordinates"""
    payload = {
        "start_lat": start_lat,
        "start_lng": start_lng,
        "end_lat": end_lat,
        "end_lng": end_lng,
        "safety_weight": safety_weight
    }
    try:
        resp = requests.post(SAFETY_ROUTE_API_URL, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": f"Safety route API error: {str(e)}"}

def load_incident_data() -> list:
    """Load incident data for heatmap visualization"""
    try:
        import pandas as pd
        # Try to load the sample data first
        try:
            df = pd.read_csv('sample_incident_data.csv')
        except FileNotFoundError:
            # If sample data not found, create some dummy data for demonstration
            print("Sample incident data not found, using dummy data")
            return [
                [37.7694, -122.4862, 1],  # Golden Gate Park area
                [37.8087, -122.4098, 2],  # Fisherman's Wharf area
                [37.7749, -122.4194, 3],  # Downtown SF
                [37.7849, -122.4094, 1],  # North Beach
                [37.7589, -122.4147, 2],  # Mission District
            ]
        
        # Filter valid coordinates
        valid_data = df[
            (df['Latitude'].notna()) & 
            (df['Longitude'].notna()) &
            (df['Latitude'] != 0) & 
            (df['Longitude'] != 0)
        ]
        
        # Convert to list of [lat, lng, weight] pairs for heatmap
        incidents = []
        for _, row in valid_data.iterrows():
            # Add weight based on incident type or severity if available
            weight = 1
            if 'Incident Category' in row:
                # Weight different incident types
                category = str(row['Incident Category']).lower()
                if 'assault' in category or 'robbery' in category:
                    weight = 3
                elif 'theft' in category or 'burglary' in category:
                    weight = 2
                else:
                    weight = 1
            
            incidents.append([float(row['Latitude']), float(row['Longitude']), weight])
        
        return incidents
    except Exception as e:
        print(f"Error loading incident data: {e}")
        # Return dummy data as fallback
        return [
            [37.7694, -122.4862, 1],
            [37.8087, -122.4098, 2],
            [37.7749, -122.4194, 3],
        ]

def create_interactive_map(route_data: dict, all_routes: list = None) -> str:
    """Create an interactive map with route and incident heatmap"""
    try:
        import folium
        from folium.plugins import HeatMap, MarkerCluster
        
        # Extract route points from the best route
        route_points = route_data.get('route_points', [])
        if not route_points:
            return "<div class='error'>No route points available for map generation</div>"
        
        # Calculate center of the route
        lats = [point[0] for point in route_points]
        lngs = [point[1] for point in route_points]
        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)
        
        # Create map with OpenStreetMap tiles
        m = folium.Map(
            location=[center_lat, center_lng], 
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Add incident heatmap
        incident_data = load_incident_data()
        if incident_data:
            HeatMap(
                incident_data,
                radius=20,
                blur=15,
                max_zoom=13,
                gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
            ).add_to(m)
        
        # Add the best route
        if route_points:
            # Create route line with safety information
            safety_score = route_data.get('safety_score', 0)
            safety_grade = route_data.get('safety_grade', 'Unknown')
            
            # Color based on safety grade
            if safety_grade == 'A':
                color = 'green'
            elif safety_grade == 'B':
                color = 'blue'
            elif safety_grade == 'C':
                color = 'orange'
            elif safety_grade == 'D':
                color = 'red'
            else:
                color = 'gray'
            
            folium.PolyLine(
                locations=route_points,
                color=color,
                weight=6,
                opacity=0.8,
                popup=f"""
                <b>Best Safe Route</b><br>
                Safety Score: {safety_score:.1f}<br>
                Safety Grade: {safety_grade}<br>
                Route Type: {route_data.get('route_type', 'Unknown')}<br>
                Time: {route_data.get('time_taken', 'Unknown')}<br>
                Incidents: {route_data.get('total_incidents', 'Unknown')}
                """
            ).add_to(m)
            
            # Add start and end markers
            folium.Marker(
                route_points[0],
                popup="<b>Start Point</b>",
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)
            
            folium.Marker(
                route_points[-1],
                popup="<b>End Point</b>",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        # Add alternative routes if available
        if all_routes:
            colors = ['purple', 'orange', 'darkblue', 'darkred', 'darkgreen']
            for i, route in enumerate(all_routes[:5]):  # Limit to 5 alternative routes
                alt_points = route.get('route_points', [])
                if alt_points and alt_points != route_points:
                    color = colors[i % len(colors)]
                    folium.PolyLine(
                        locations=alt_points,
                        color=color,
                        weight=3,
                        opacity=0.5,
                        popup=f"""
                        <b>Alternative Route {i+1}</b><br>
                        Safety Score: {route.get('safety_score', 'Unknown')}<br>
                        Safety Grade: {route.get('safety_grade', 'Unknown')}<br>
                        Route Type: {route.get('route_type', 'Unknown')}
                        """
                    ).add_to(m)
        
        # Add safety zones (circles around route points with safety scores)
        if route_data.get('stops'):
            for stop in route_data['stops']:
                coords = stop.get('coordinates', [])
                if coords:
                    safety_score = stop.get('safety_score', 50)
                    incident_count = stop.get('incident_count', 0)
                    
                    # Color based on safety score
                    if safety_score >= 80:
                        fill_color = 'green'
                    elif safety_score >= 60:
                        fill_color = 'blue'
                    elif safety_score >= 40:
                        fill_color = 'orange'
                    else:
                        fill_color = 'red'
                    
                    folium.CircleMarker(
                        location=coords,
                        radius=8,
                        popup=f"""
                        <b>Safety Zone</b><br>
                        Safety Score: {safety_score:.1f}<br>
                        Incidents: {incident_count}<br>
                        Stop: {stop.get('stop_name', 'Unknown')}
                        """,
                        color=fill_color,
                        fill=True,
                        fillOpacity=0.7
                    ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 220px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; color: black; border-radius: 8px;">
        <p style="margin:0; padding-bottom: 5px;"><b>Map Legend</b></p>
        <p style="margin:0;"><i class="fa fa-circle" style="color:green"></i> Best Route (A Grade)</p>
        <p style="margin:0;"><i class="fa fa-circle" style="color:blue"></i> Good Route (B Grade)</p>
        <p style="margin:0;"><i class="fa fa-circle" style="color:orange"></i> Moderate Route (C Grade)</p>
        <p style="margin:0;"><i class="fa fa-circle" style="color:red"></i> Poor Route (D Grade)</p>
        <p style="margin:0;"><i class="fa fa-fire" style="color:red"></i> Incident Heatmap</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map to temporary file and return HTML
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            map_path = f.name
        
        m.save(map_path)
        
        # Read the HTML content
        with open(map_path, 'r') as f:
            map_html = f.read()
        
        # Clean up temporary file
        os.unlink(map_path)
        
        return map_html
        
    except ImportError:
        return "<div class='error'>Folium not available. Install with: pip install folium</div>"
    except Exception as e:
        return f"<div class='error'>Error generating map: {str(e)}</div>"

def format_safety_output(result: dict) -> (str, str):
    """Formats safety output and returns a tuple: (details_html, map_html)"""
    if not result.get("success", False):
        error_html = f"<div class='error'>{result.get('message', 'Unknown error')}</div>"
        return error_html, ""
    
    data = result.get("data") or result
    best = data.get("best_route", {})
    safe_routes = data.get("safe_routes", [])
    analysis = data.get("safety_analysis", {})
    
    # --- Details HTML ---
    details_html = f"<h3>Best Safe Route: {best.get('route_id', '')}</h3>"
    details_html += f"<b>Safety Score:</b> {best.get('safety_score', '')} ({best.get('safety_grade', '')})<br>"
    details_html += f"<b>Time Taken:</b> {best.get('time_taken', '')} | <b>Incidents:</b> {best.get('total_incidents', '')}<br>"
    details_html += f"<b>Stops:</b><ul>"
    for stop in best.get('stops', []):
        details_html += f"<li>{stop.get('stop_number')}: {stop.get('stop_name')} (Safety: {stop.get('safety_score')}, Incidents: {stop.get('incident_count')})</li>"
    details_html += "</ul>"
    
    details_html += f"<h4>All Safe Route Options</h4>"
    for route in safe_routes:
        details_html += f"<div style='border:1px solid #ccc; border-radius:8px; padding:10px; margin-bottom:10px;'>"
        details_html += f"<b>Route ID:</b> {route.get('route_id')} | <b>Type:</b> {route.get('route_type', '')}<br>"
        details_html += f"<b>Safety Score:</b> {route.get('safety_score', '')} ({route.get('safety_grade', '')}) | <b>Incidents:</b> {route.get('total_incidents', '')}<br>"
        details_html += f"<b>Time Taken:</b> {route.get('time_taken', '')} | <b>Cost:</b> ${route.get('cost', '')}<br>"
        details_html += f"<b>Total Stops:</b> {route.get('total_stops', '')}"
        details_html += "</div>"
    
    if analysis:
        details_html += f"<h4>Safety Analysis</h4><pre>{json.dumps(analysis, indent=2)}</pre>"

    # --- Map HTML ---
    map_html = ""
    if best.get('route_points'):
        map_html = create_interactive_map(best, safe_routes)
        # Wrap map in a container with a fixed height to ensure it's visible
        map_html = f"<div style='height: 500px; border: 2px solid #ddd; border-radius: 8px;'>{map_html}</div>"

    return details_html, map_html

def safety_interface(user_request: str, safety_weight: float) -> (str, str):
    result = get_safety_route(user_request, safety_weight)
    return format_safety_output(result)

def safety_interface_with_coords(start_lat: float, start_lng: float, end_lat: float, end_lng: float, safety_weight: float) -> (str, str):
    """Interface function for safety tab with direct coordinates"""
    result = get_safety_route_with_coords(start_lat, start_lng, end_lat, end_lng, safety_weight)
    return format_safety_output(result)

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
            gr.Markdown("## Transport Route Planner")
            with gr.Row():
                transport_user_request = gr.Textbox(
                    label="Describe your transit need", 
                    placeholder="e.g., Get me from SFO to Embarcadero by 9am"
                )
                transport_origin = gr.Textbox(
                    label="Origin", placeholder="e.g., SFO"
                )
                transport_destination = gr.Textbox(
                    label="Destination", placeholder="e.g., EMB"
                )
                transport_time = gr.Textbox(
                    label="Time", placeholder="e.g., 09:00"
                )
            transport_button = gr.Button("Find Transit Routes", variant="primary")
            transport_output = gr.HTML("", label="Transit Options")
            transport_button.click(
                fn=transport_interface,
                inputs=[transport_user_request, transport_origin, transport_destination, transport_time],
                outputs=transport_output
            )
        
        with gr.TabItem("Safety"):
            gr.Markdown("## Safety Route Finder with Interactive Map")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Option 1: Natural Language")
                    safety_user_request = gr.Textbox(
                        label="Describe your route (or enter coordinates)",
                        placeholder="e.g., Find safe route from 37.7694,-122.4862 to 37.8087,-122.4098"
                    )
                    safety_weight = gr.Slider(
                        label="Safety Weight (0=Fastest, 1=Safest)",
                        minimum=0.0, maximum=1.0, value=0.7, step=0.05
                    )
                    safety_button = gr.Button("Find Safe Route", variant="primary")
                
                with gr.Column():
                    gr.Markdown("### Option 2: Direct Coordinates")
                    with gr.Row():
                        start_lat = gr.Number(label="Start Latitude", value=37.7694, precision=6)
                        start_lng = gr.Number(label="Start Longitude", value=-122.4862, precision=6)
                    with gr.Row():
                        end_lat = gr.Number(label="End Latitude", value=37.8087, precision=6)
                        end_lng = gr.Number(label="End Longitude", value=-122.4098, precision=6)
                    safety_weight_coords = gr.Slider(
                        label="Safety Weight (0=Fastest, 1=Safest)",
                        minimum=0.0, maximum=1.0, value=0.7, step=0.05
                    )
                    safety_coords_button = gr.Button("Find Safe Route (Coordinates)", variant="primary")
            
            gr.Markdown("### Route Results")
            # Create two separate HTML components for details and the map
            safety_details_output = gr.HTML(label="Route Details")
            safety_map_output = gr.HTML(label="Interactive Map")
            
            # Connect both buttons to the new interface functions
            safety_button.click(
                fn=safety_interface,
                inputs=[safety_user_request, safety_weight],
                outputs=[safety_details_output, safety_map_output]
            )
            
            safety_coords_button.click(
                fn=safety_interface_with_coords,
                inputs=[start_lat, start_lng, end_lat, end_lng, safety_weight_coords],
                outputs=[safety_details_output, safety_map_output]
            )

# Launch the app
if __name__ == "__main__":
    app.launch(share=False)
