from flask import Flask, render_template, request, jsonify
from safe_route_finder import SafeRouteFinder
import os
import json

app = Flask(__name__)

# Initialize the route finder
route_finder = None

def initialize_route_finder():
    """Initialize the route finder with police data"""
    global route_finder
    if route_finder is None:
        csv_file = 'Police_Department_Incident_Reports__2018_to_Present_20250621.csv'
        if os.path.exists(csv_file):
            route_finder = SafeRouteFinder(csv_file)
            print("Route finder initialized successfully!")
        else:
            print(f"Warning: {csv_file} not found. Please ensure the police data file is in the current directory.")

@app.route('/')
def index():
    """Main page with route finder interface"""
    return render_template('index.html')

@app.route('/find_route', methods=['POST'])
def find_route():
    """API endpoint to find safe route"""
    try:
        data = request.get_json()
        
        # Extract coordinates
        start_lat = float(data['start_lat'])
        start_lng = float(data['start_lng'])
        end_lat = float(data['end_lat'])
        end_lng = float(data['end_lng'])
        
        # Optional parameters
        safety_weight = float(data.get('safety_weight', 0.7))
        max_distance_factor = float(data.get('max_distance_factor', 1.5))
        
        # Find the route
        route = route_finder.find_safe_route(
            start_lat, start_lng, end_lat, end_lng,
            max_distance_factor=max_distance_factor,
            safety_weight=safety_weight
        )
        
        if route:
            # Get route summary and recommendations
            summary = route_finder.get_route_summary(route)
            recommendations = route_finder.get_safety_recommendations(route)
            
            # Convert route to JSON-serializable format
            route_data = []
            for point in route:
                route_data.append({
                    'lat': point.lat,
                    'lng': point.lng,
                    'safety_score': point.safety_score,
                    'incident_count': point.incident_count,
                    'distance_from_start': point.distance_from_start
                })
            
            return jsonify({
                'success': True,
                'route': route_data,
                'summary': summary,
                'recommendations': recommendations
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No route found'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/get_safety_info', methods=['POST'])
def get_safety_info():
    """Get safety information for a specific location"""
    try:
        data = request.get_json()
        lat = float(data['lat'])
        lng = float(data['lng'])
        
        safety_score = route_finder.get_safety_score(lat, lng)
        incident_count = route_finder.get_incident_count(lat, lng)
        
        return jsonify({
            'success': True,
            'safety_score': safety_score,
            'incident_count': incident_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/create_map', methods=['POST'])
def create_map():
    """Create and save an interactive map"""
    try:
        data = request.get_json()
        route_data = data['route']
        start_name = data.get('start_name', 'Start')
        end_name = data.get('end_name', 'End')
        
        # Convert route data back to RoutePoint objects
        from safe_route_finder import RoutePoint
        route = []
        for point_data in route_data:
            route.append(RoutePoint(
                lat=point_data['lat'],
                lng=point_data['lng'],
                safety_score=point_data['safety_score'],
                incident_count=point_data['incident_count'],
                distance_from_start=point_data['distance_from_start'],
                total_distance=point_data['distance_from_start']
            ))
        
        # Create map
        map_obj = route_finder.visualize_route(route, start_name, end_name)
        map_filename = 'static/safe_route_map.html'
        map_obj.save(map_filename)
        
        return jsonify({
            'success': True,
            'map_url': '/static/safe_route_map.html'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # Initialize route finder
    initialize_route_finder()
    
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 