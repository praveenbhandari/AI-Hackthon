from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import numpy as np
from google_maps_router import GoogleMapsRouter
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the Google Maps router
print("Initializing route finder...")
route_finder = GoogleMapsRouter('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')
print("Route finder initialized successfully!")

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/find_route', methods=['POST'])
def find_route():
    """Find the optimal safe route using Google Maps"""
    try:
        data = request.get_json()
        
        # Extract parameters
        start_lat = float(data['start_lat'])
        start_lng = float(data['start_lng'])
        end_lat = float(data['end_lat'])
        end_lng = float(data['end_lng'])
        safety_weight = float(data.get('safety_weight', 0.7))  # Default to 70% safety focus
        max_distance_factor = float(data.get('max_distance_factor', 2.0))  # Default to 2x direct distance
        
        print(f"Finding route with safety weight: {safety_weight}")
        print(f"From: ({start_lat:.4f}, {start_lng:.4f})")
        print(f"To: ({end_lat:.4f}, {end_lng:.4f})")
        
        # Find optimal route with timeout protection
        start_time = time.time()
        result = route_finder.find_google_route(
            start_lat, start_lng, end_lat, end_lng,
            safety_weight=safety_weight,
            max_distance_factor=max_distance_factor
        )
        elapsed_time = time.time() - start_time
        
        print(f"Route finding completed in {elapsed_time:.2f} seconds")
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to find route')
            }), 500
        
        # Convert numpy types for JSON serialization
        response_data = convert_numpy_types({
            'success': True,
            'best_route': {
                'route_type': result['best_route'].route_type,
                'total_distance': result['best_route'].total_distance,
                'total_duration': result['best_route'].total_duration,
                'avg_safety_score': result['best_route'].avg_safety_score,
                'total_incidents': result['best_route'].total_incidents,
                'safety_grade': result['best_route'].safety_grade,
                'waypoints': result['best_route'].waypoints,
                'route_points': result['best_route'].route_points,
                'steps': [
                    {
                        'instruction': step.instruction,
                        'distance': step.distance,
                        'duration': step.duration,
                        'maneuver': step.maneuver,
                        'safety_score': step.safety_score,
                        'incident_count': step.incident_count,
                        'start_location': step.start_location,
                        'end_location': step.end_location
                    }
                    for step in result['best_route'].steps
                ]
            },
            'all_options': [
                {
                    'route_type': option.route_type,
                    'total_distance': option.total_distance,
                    'total_duration': option.total_duration,
                    'avg_safety_score': option.avg_safety_score,
                    'total_incidents': option.total_incidents,
                    'safety_grade': option.safety_grade,
                    'waypoints': option.waypoints,
                    'route_points': option.route_points,
                    'steps': [
                        {
                            'instruction': step.instruction,
                            'distance': step.distance,
                            'duration': step.duration,
                            'maneuver': step.maneuver,
                            'safety_score': step.safety_score,
                            'incident_count': step.incident_count,
                            'start_location': step.start_location,
                            'end_location': step.end_location
                        }
                        for step in option.steps
                    ]
                }
                for option in result['all_options']
            ],
            'routing_method': result['routing_method'],
            'elapsed_time': elapsed_time,
            'generation_time': result.get('generation_time', elapsed_time)
        })
        
        print(f"✅ Route found successfully! Method: {result['routing_method']}")
        print(f"⏱️  Total time: {elapsed_time:.2f}s, Generation time: {result.get('generation_time', elapsed_time):.2f}s")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error finding route: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/get_safety_info', methods=['POST'])
def get_safety_info():
    """Get safety information for a specific location"""
    try:
        data = request.get_json()
        lat = float(data['lat'])
        lng = float(data['lng'])
        
        # Get safety score and nearby incidents
        safety_score = route_finder.get_safety_score(lat, lng)
        nearby_incidents = route_finder._count_nearby_incidents(lat, lng, radius_meters=500)
        
        return jsonify({
            'success': True,
            'safety_score': float(safety_score),
            'safety_grade': route_finder.get_safety_grade(safety_score),
            'nearby_incidents': int(nearby_incidents)
        })
        
    except Exception as e:
        print(f"Error getting safety info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/visualize_routes', methods=['POST'])
def visualize_routes():
    """Create a map visualization of all route options"""
    try:
        data = request.get_json()
        start_lat = float(data['start_lat'])
        start_lng = float(data['start_lng'])
        end_lat = float(data['end_lat'])
        end_lng = float(data['end_lng'])
        safety_weight = float(data.get('safety_weight', 0.7))
        
        print("Creating route visualization...")
        
        # Find routes
        result = route_finder.find_google_route(
            start_lat, start_lng, end_lat, end_lng,
            safety_weight=safety_weight
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to find routes')
            }), 500
        
        # Create visualization
        map_obj = route_finder.visualize_google_routes(
            result['all_options'],
            "Start Location",
            "End Location"
        )
        
        # Save map to file
        map_filename = f"google_maps_routes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        map_path = os.path.join('static', 'maps', map_filename)
        os.makedirs(os.path.dirname(map_path), exist_ok=True)
        map_obj.save(map_path)
        
        print(f"Map saved as {map_filename}")
        
        return jsonify({
            'success': True,
            'map_url': f'/static/maps/{map_filename}'
        })
        
    except Exception as e:
        print(f"Error creating visualization: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/check_google_maps_availability')
def check_google_maps_availability():
    """Check if Google Maps integration is available"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return jsonify({
        'available': api_key is not None,
        'message': 'Google Maps API key configured' if api_key else 'Google Maps API key not found - using simulated routes'
    })

@app.route('/get_incident_data')
def get_incident_data():
    """Get incident data for heatmap visualization"""
    try:
        # Get valid incident data
        valid_data = route_finder.incident_data[
            (route_finder.incident_data['Latitude'].notna()) & 
            (route_finder.incident_data['Longitude'].notna()) &
            (route_finder.incident_data['Latitude'] != 0) & 
            (route_finder.incident_data['Longitude'] != 0)
        ]
        
        # Sample data for performance (limit to 1000 points)
        if len(valid_data) > 1000:
            valid_data = valid_data.sample(n=1000, random_state=42)
        
        incidents = []
        for _, row in valid_data.iterrows():
            incidents.append({
                'lat': float(row['Latitude']),
                'lng': float(row['Longitude'])
            })
        
        return jsonify({
            'success': True,
            'incidents': incidents,
            'total_incidents': len(incidents)
        })
        
    except Exception as e:
        print(f"Error getting incident data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'route_finder_initialized': route_finder is not None,
        'incident_data_loaded': not route_finder.incident_data.empty if route_finder else False
    })

if __name__ == '__main__':
    print("Starting Flask web server...")
    app.run(debug=True, host='0.0.0.0', port=8000) 