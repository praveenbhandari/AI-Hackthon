import requests
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import time
from safe_route_finder import RoutePoint, SafeRouteFinder

@dataclass
class GoogleRouteStep:
    """Represents a step in Google Maps directions"""
    instruction: str
    distance: str
    duration: str
    start_location: Tuple[float, float]
    end_location: Tuple[float, float]
    maneuver: str
    safety_score: float = 0.0
    incident_count: int = 0

class GoogleMapsRouter:
    def __init__(self, api_key: str = None):
        """
        Initialize Google Maps router
        
        Args:
            api_key: Google Maps API key. If None, will try to use environment variable
        """
        self.api_key = api_key or self._get_api_key()
        self.base_url = "https://maps.googleapis.com/maps/api/directions/json"
        self.safety_finder = None
        
    def _get_api_key(self) -> str:
        """Get API key from environment variable"""
        import os
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            raise ValueError(
                "Google Maps API key not found. Please set GOOGLE_MAPS_API_KEY "
                "environment variable or pass api_key parameter."
            )
        return api_key
    
    def set_safety_finder(self, safety_finder: SafeRouteFinder):
        """Set the safety finder for route analysis"""
        self.safety_finder = safety_finder
    
    def get_route(self, 
                  start_lat: float, 
                  start_lng: float, 
                  end_lat: float, 
                  end_lng: float,
                  mode: str = "walking",
                  avoid: List[str] = None) -> Dict:
        """
        Get route from Google Maps Directions API
        
        Args:
            start_lat, start_lng: Starting coordinates
            end_lat, end_lng: Ending coordinates
            mode: Travel mode (walking, driving, bicycling, transit)
            avoid: List of features to avoid (tolls, highways, ferries)
        
        Returns:
            Dictionary containing route information
        """
        params = {
            'origin': f"{start_lat},{start_lng}",
            'destination': f"{end_lat},{end_lng}",
            'mode': mode,
            'key': self.api_key
        }
        
        if avoid:
            params['avoid'] = '|'.join(avoid)
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'OK':
                raise Exception(f"Google Maps API error: {data['status']}")
            
            return data
            
        except requests.RequestException as e:
            raise Exception(f"Failed to get route from Google Maps: {str(e)}")
    
    def parse_google_route(self, google_data: Dict) -> List[GoogleRouteStep]:
        """Parse Google Maps route data into route steps"""
        if not google_data.get('routes'):
            return []
        
        route = google_data['routes'][0]
        steps = []
        
        for leg in route['legs']:
            for step in leg['steps']:
                # Extract step information
                instruction = step.get('html_instructions', '')
                distance = step.get('distance', {}).get('text', '')
                duration = step.get('duration', {}).get('text', '')
                
                # Get start and end locations
                start_lat = step['start_location']['lat']
                start_lng = step['start_location']['lng']
                end_lat = step['end_location']['lat']
                end_lng = step['end_location']['lng']
                
                # Get maneuver type
                maneuver = step.get('maneuver', 'straight')
                
                # Create route step
                route_step = GoogleRouteStep(
                    instruction=instruction,
                    distance=distance,
                    duration=duration,
                    start_location=(start_lat, start_lng),
                    end_location=(end_lat, end_lng),
                    maneuver=maneuver
                )
                
                steps.append(route_step)
        
        return steps
    
    def enhance_route_with_safety(self, google_steps: List[GoogleRouteStep]) -> List[RoutePoint]:
        """Enhance Google Maps route with safety analysis"""
        if not self.safety_finder:
            raise Exception("Safety finder not set. Call set_safety_finder() first.")
        
        route_points = []
        total_distance = 0
        
        for i, step in enumerate(google_steps):
            start_lat, start_lng = step.start_location
            end_lat, end_lng = step.end_location
            
            # Get safety information for the step
            safety_score = self.safety_finder.get_safety_score(start_lat, start_lng)
            incident_count = self.safety_finder.get_incident_count(start_lat, start_lng)
            
            # Calculate distance for this step
            step_distance = self.safety_finder.calculate_distance(
                start_lat, start_lng, end_lat, end_lng
            )
            total_distance += step_distance
            
            # Create route point
            route_point = RoutePoint(
                lat=start_lat,
                lng=start_lng,
                safety_score=safety_score,
                incident_count=incident_count,
                distance_from_start=total_distance - step_distance,
                total_distance=total_distance
            )
            
            route_points.append(route_point)
            
            # Add end point of the step
            end_safety_score = self.safety_finder.get_safety_score(end_lat, end_lng)
            end_incident_count = self.safety_finder.get_incident_count(end_lat, end_lng)
            
            end_route_point = RoutePoint(
                lat=end_lat,
                lng=end_lng,
                safety_score=end_safety_score,
                incident_count=end_incident_count,
                distance_from_start=total_distance,
                total_distance=total_distance
            )
            
            route_points.append(end_route_point)
        
        return route_points
    
    def get_safe_route(self, 
                      start_lat: float, 
                      start_lng: float, 
                      end_lat: float, 
                      end_lng: float,
                      safety_finder: SafeRouteFinder,
                      mode: str = "walking") -> Dict:
        """
        Get a safe route using Google Maps with safety analysis
        
        Args:
            start_lat, start_lng: Starting coordinates
            end_lat, end_lng: Ending coordinates
            safety_finder: SafetyRouteFinder instance
            mode: Travel mode
        
        Returns:
            Dictionary with route information including safety analysis
        """
        self.set_safety_finder(safety_finder)
        
        # Get route from Google Maps
        google_data = self.get_route(start_lat, start_lng, end_lat, end_lng, mode)
        
        # Parse Google route
        google_steps = self.parse_google_route(google_data)
        
        # Enhance with safety analysis
        route_points = self.enhance_route_with_safety(google_steps)
        
        # Get route summary
        summary = safety_finder.get_route_summary(route_points)
        recommendations = safety_finder.get_safety_recommendations(route_points)
        
        return {
            'google_data': google_data,
            'google_steps': google_steps,
            'route_points': route_points,
            'summary': summary,
            'recommendations': recommendations
        }

# Example usage
def main():
    """Example of using Google Maps router with safety analysis"""
    
    # Initialize safety finder
    safety_finder = SafeRouteFinder('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')
    
    # Initialize Google Maps router
    # Note: You need to set GOOGLE_MAPS_API_KEY environment variable
    try:
        router = GoogleMapsRouter()
        
        # Example coordinates in San Francisco
        start_lat, start_lng = 37.7694, -122.4862  # Golden Gate Park
        end_lat, end_lng = 37.8087, -122.4098      # Fisherman's Wharf
        
        print("Getting route from Google Maps with safety analysis...")
        
        # Get safe route
        result = router.get_safe_route(
            start_lat, start_lng, end_lat, end_lng, safety_finder
        )
        
        # Display results
        print(f"\n=== Google Maps Route with Safety Analysis ===")
        print(f"Total distance: {result['summary']['total_distance_meters']:.0f} meters")
        print(f"Safety grade: {result['summary']['safety_grade']}")
        print(f"Average safety score: {result['summary']['avg_safety_score']:.1f}")
        
        print(f"\n=== Turn-by-Turn Directions ===")
        for i, step in enumerate(result['google_steps'][:5]):  # Show first 5 steps
            print(f"{i+1}. {step.instruction}")
            print(f"   Distance: {step.distance}, Duration: {step.duration}")
            print(f"   Safety: {result['route_points'][i*2].safety_score:.1f}")
            print()
        
        print(f"\n=== Safety Recommendations ===")
        for rec in result['recommendations']:
            print(f"• {rec}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nTo use Google Maps integration:")
        print("1. Get a Google Maps API key from Google Cloud Console")
        print("2. Enable Directions API")
        print("3. Set environment variable: export GOOGLE_MAPS_API_KEY='your_api_key'")

if __name__ == "__main__":
    main() 