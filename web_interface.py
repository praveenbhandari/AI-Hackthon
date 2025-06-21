from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import numpy as np
from enhanced_route_finder import EnhancedRouteFinder
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the enhanced route finder
route_finder = EnhancedRouteFinder('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')

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
    """Find the optimal safe route using enhanced route finder"""
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
        
        # Find optimal route using enhanced route finder
        result = route_finder.find_optimal_safe_route(
            start_lat, start_lng, end_lat, end_lng,
            safety_weight=safety_weight,
            max_distance_factor=max_distance_factor
        )
        
        # Convert numpy types for JSON serialization
        response_data = convert_numpy_types({
            'success': True,
            'best_route': {
                'route_type': result['best_route'].route_type,
                'total_distance': result['best_route'].total_distance,
                'avg_safety_score': result['best_route'].avg_safety_score,
                'total_incidents': result['best_route'].total_incidents,
                'safety_grade': result['best_route'].safety_grade,
                'waypoints': result['best_route'].waypoints,
                'route_points': [(point.lat, point.lng) for point in result['best_route'].route]
            },
            'route_comparison': result['route_comparison'],
            'summary': result['summary'],
            'recommendations': result['recommendations'],
            'all_options': [
                {
                    'route_type': option.route_type,
                    'total_distance': option.total_distance,
                    'avg_safety_score': option.avg_safety_score,
                    'total_incidents': option.total_incidents,
                    'safety_grade': option.safety_grade,
                    'waypoints': option.waypoints,
                    'route_points': [(point.lat, point.lng) for point in option.route]
                }
                for option in result['all_options']
            ]
        })
        
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
        nearby_incidents = route_finder.get_nearby_incidents(lat, lng, radius_meters=500)
        
        return jsonify({
            'success': True,
            'safety_score': float(safety_score),
            'safety_grade': route_finder.get_safety_grade(safety_score),
            'nearby_incidents': convert_numpy_types(nearby_incidents)
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
        
        # Find routes
        result = route_finder.find_optimal_safe_route(
            start_lat, start_lng, end_lat, end_lng,
            safety_weight=safety_weight
        )
        
        # Create visualization
        map_obj = route_finder.visualize_all_routes(
            result['all_options'],
            "Start Location",
            "End Location"
        )
        
        # Save map to file
        map_filename = f"route_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        map_path = os.path.join('static', 'maps', map_filename)
        os.makedirs(os.path.dirname(map_path), exist_ok=True)
        map_obj.save(map_path)
        
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 