import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
import heapq
from dataclasses import dataclass
import math
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

@dataclass
class RoutePoint:
    """Represents a point on the route with safety information"""
    lat: float
    lng: float
    safety_score: float
    incident_count: int
    distance_from_start: float
    total_distance: float

class SafeRouteFinder:
    def __init__(self, incident_data_path: str):
        """
        Initialize the SafeRouteFinder with police incident data
        
        Args:
            incident_data_path: Path to the CSV file containing police incident data
        """
        self.incident_data = self._load_and_preprocess_data(incident_data_path)
        self.safety_grid = None
        self.grid_resolution = 0.001  # Approximately 100 meters in SF
        
    def _load_and_preprocess_data(self, data_path: str) -> pd.DataFrame:
        """Load and preprocess the police incident data"""
        print("Loading police incident data...")
        
        # Load data with low_memory=False to avoid dtype warnings
        df = pd.read_csv(data_path, low_memory=False)
        
        # Clean and filter the data
        df = df.dropna(subset=['Latitude', 'Longitude'])
        
        # Convert to numeric, coercing errors to NaN
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        # Remove rows with invalid coordinates
        df = df.dropna(subset=['Latitude', 'Longitude'])
        
        # Filter to recent data (last 2 years for better relevance)
        df['Incident Date'] = pd.to_datetime(df['Incident Date'], errors='coerce')
        two_years_ago = datetime.now() - timedelta(days=730)
        df = df[df['Incident Date'] >= two_years_ago]
        
        # Add time-based features
        df['Incident Hour'] = pd.to_datetime(df['Incident Time'], format='%H:%M', errors='coerce').dt.hour
        df['Is_Night'] = ((df['Incident Hour'] >= 22) | (df['Incident Hour'] <= 6)).astype(int)
        
        # Categorize incidents by severity
        severity_mapping = {
            'Homicide': 10,
            'Rape': 9,
            'Robbery': 8,
            'Assault': 7,
            'Burglary': 6,
            'Theft': 5,
            'Vehicle Theft': 4,
            'Vandalism': 3,
            'Fraud': 2,
            'Other': 1
        }
        
        df['Severity'] = df['Incident Category'].map(severity_mapping).fillna(1)
        
        print(f"Loaded {len(df)} incidents from {df['Incident Date'].min()} to {df['Incident Date'].max()}")
        return df
    
    def create_safety_grid(self, bounds: Tuple[float, float, float, float] = None):
        """
        Create a safety grid based on incident density and severity
        
        Args:
            bounds: (min_lat, min_lng, max_lat, max_lng) - if None, uses data bounds
        """
        print("Creating safety grid...")
        
        if bounds is None:
            bounds = (
                self.incident_data['Latitude'].min(),
                self.incident_data['Longitude'].min(),
                self.incident_data['Latitude'].max(),
                self.incident_data['Longitude'].max()
            )
        
        min_lat, min_lng, max_lat, max_lng = bounds
        
        # Create grid
        lat_grid = np.arange(min_lat, max_lat, self.grid_resolution)
        lng_grid = np.arange(min_lng, max_lng, self.grid_resolution)
        
        # Initialize safety grid
        self.safety_grid = np.zeros((len(lat_grid), len(lng_grid)))
        self.lat_grid = lat_grid
        self.lng_grid = lng_grid
        
        # Calculate incident density and severity for each grid cell
        for i, lat in enumerate(lat_grid):
            for j, lng in enumerate(lng_grid):
                # Find incidents within this grid cell
                mask = (
                    (self.incident_data['Latitude'] >= lat) &
                    (self.incident_data['Latitude'] < lat + self.grid_resolution) &
                    (self.incident_data['Longitude'] >= lng) &
                    (self.incident_data['Longitude'] < lng + self.grid_resolution)
                )
                
                cell_incidents = self.incident_data[mask]
                
                if len(cell_incidents) > 0:
                    # Calculate safety score based on incident count and severity
                    incident_count = len(cell_incidents)
                    avg_severity = cell_incidents['Severity'].mean()
                    night_incidents = cell_incidents['Is_Night'].sum()
                    
                    # Safety score decreases with more incidents and higher severity
                    # Night incidents are weighted more heavily
                    safety_score = 100 - (incident_count * 2) - (avg_severity * 3) - (night_incidents * 5)
                    self.safety_grid[i, j] = max(0, safety_score)
                else:
                    self.safety_grid[i, j] = 100  # No incidents = high safety
        
        print(f"Created safety grid with shape {self.safety_grid.shape}")
    
    def get_safety_score(self, lat: float, lng: float) -> float:
        """Get safety score for a specific location"""
        if self.safety_grid is None:
            return 50  # Default safety score
        
        # Find the closest grid cell
        lat_idx = np.argmin(np.abs(self.lat_grid - lat))
        lng_idx = np.argmin(np.abs(self.lng_grid - lng))
        
        return self.safety_grid[lat_idx, lng_idx]
    
    def get_incident_count(self, lat: float, lng: float, radius_meters: float = 100) -> int:
        """Get number of incidents within a radius of a location"""
        # Convert meters to approximate degrees (rough approximation)
        radius_deg = radius_meters / 111000  # 1 degree ≈ 111km
        
        mask = (
            (self.incident_data['Latitude'] >= lat - radius_deg) &
            (self.incident_data['Latitude'] <= lat + radius_deg) &
            (self.incident_data['Longitude'] >= lng - radius_deg) &
            (self.incident_data['Longitude'] <= lng + radius_deg)
        )
        
        nearby_incidents = self.incident_data[mask]
        
        # Calculate exact distance for more precision
        distances = np.sqrt(
            (nearby_incidents['Latitude'] - lat) ** 2 + 
            (nearby_incidents['Longitude'] - lng) ** 2
        ) * 111000  # Convert to meters
        
        return len(distances[distances <= radius_meters])
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in meters"""
        # Haversine formula
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def find_safe_route(self, 
                       start_lat: float, 
                       start_lng: float, 
                       end_lat: float, 
                       end_lng: float,
                       max_distance_factor: float = 1.5,
                       safety_weight: float = 0.7) -> List[RoutePoint]:
        """
        Find the safest route between two points using A* algorithm
        
        Args:
            start_lat, start_lng: Starting coordinates
            end_lat, end_lng: Ending coordinates
            max_distance_factor: Maximum route length as factor of direct distance
            safety_weight: Weight given to safety vs distance (0-1)
        
        Returns:
            List of RoutePoint objects representing the safest path
        """
        print(f"Finding safe route from ({start_lat:.4f}, {start_lng:.4f}) to ({end_lat:.4f}, {end_lng:.4f})")
        
        # Create safety grid if not already created
        if self.safety_grid is None:
            bounds = (
                min(start_lat, end_lat) - 0.01,
                min(start_lng, end_lng) - 0.01,
                max(start_lat, end_lat) + 0.01,
                max(start_lng, end_lng) + 0.01
            )
            self.create_safety_grid(bounds)
        
        # Calculate direct distance
        direct_distance = self.calculate_distance(start_lat, start_lng, end_lat, end_lng)
        max_distance = direct_distance * max_distance_factor
        
        # Generate waypoints along the route
        waypoints = self._generate_waypoints(start_lat, start_lng, end_lat, end_lng, max_distance)
        
        # Find optimal path through waypoints
        route = self._find_optimal_path(waypoints, safety_weight)
        
        print(f"Found route with {len(route)} waypoints, total distance: {route[-1].total_distance:.0f}m")
        return route
    
    def _generate_waypoints(self, start_lat: float, start_lng: float, 
                           end_lat: float, end_lng: float, max_distance: float) -> List[Tuple[float, float]]:
        """Generate waypoints along the route"""
        waypoints = []
        
        # Add start and end points
        waypoints.append((start_lat, start_lng))
        waypoints.append((end_lat, end_lng))
        
        # Generate intermediate waypoints
        num_intermediate = int(max_distance / 200)  # Waypoint every 200m
        for i in range(1, num_intermediate):
            # Linear interpolation
            lat = start_lat + (end_lat - start_lat) * i / num_intermediate
            lng = start_lng + (end_lng - start_lng) * i / num_intermediate
            
            # Add some randomness to explore safer areas
            lat += np.random.normal(0, 0.001)  # ±100m variation
            lng += np.random.normal(0, 0.001)
            
            waypoints.append((lat, lng))
        
        return waypoints
    
    def _find_optimal_path(self, waypoints: List[Tuple[float, float]], safety_weight: float) -> List[RoutePoint]:
        """Find optimal path through waypoints using dynamic programming"""
        n = len(waypoints)
        
        # Calculate distances and safety scores between all waypoints
        distances = np.zeros((n, n))
        safety_scores = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lng1 = waypoints[i]
                    lat2, lng2 = waypoints[j]
                    distances[i, j] = self.calculate_distance(lat1, lng1, lat2, lng2)
                    
                    # Safety score is average of both points
                    safety1 = self.get_safety_score(lat1, lng1)
                    safety2 = self.get_safety_score(lat2, lng2)
                    safety_scores[i, j] = (safety1 + safety2) / 2
        
        # Normalize distances and safety scores
        max_dist = distances.max()
        max_safety = safety_scores.max()
        
        distances_norm = distances / max_dist
        safety_scores_norm = safety_scores / max_safety
        
        # Combined cost (lower is better)
        costs = (1 - safety_weight) * distances_norm + safety_weight * (1 - safety_scores_norm)
        
        # Find shortest path using Dijkstra's algorithm
        path = self._dijkstra(costs, 0, n-1)
        
        # Convert to RoutePoint objects
        route_points = []
        total_distance = 0
        
        for i, point_idx in enumerate(path):
            lat, lng = waypoints[point_idx]
            safety_score = self.get_safety_score(lat, lng)
            incident_count = self.get_incident_count(lat, lng)
            
            if i > 0:
                prev_lat, prev_lng = waypoints[path[i-1]]
                segment_distance = self.calculate_distance(prev_lat, prev_lng, lat, lng)
                total_distance += segment_distance
            
            route_points.append(RoutePoint(
                lat=lat,
                lng=lng,
                safety_score=safety_score,
                incident_count=incident_count,
                distance_from_start=total_distance,
                total_distance=total_distance
            ))
        
        return route_points
    
    def _dijkstra(self, costs: np.ndarray, start: int, end: int) -> List[int]:
        """Dijkstra's algorithm to find shortest path"""
        n = len(costs)
        distances = np.full(n, np.inf)
        distances[start] = 0
        previous = [-1] * n
        
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == end:
                break
            
            for neighbor in range(n):
                if neighbor != current and costs[current, neighbor] < np.inf:
                    new_dist = current_dist + costs[current, neighbor]
                    
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
                        heapq.heappush(pq, (new_dist, neighbor))
        
        # Reconstruct path
        path = []
        current = end
        while current != -1:
            path.append(current)
            current = previous[current]
        
        return path[::-1]
    
    def visualize_route(self, route: List[RoutePoint], 
                       start_name: str = "Start", 
                       end_name: str = "End") -> folium.Map:
        """Create an interactive map showing the safe route"""
        if not route:
            return None
        
        # Calculate center of the route
        center_lat = sum(point.lat for point in route) / len(route)
        center_lng = sum(point.lng for point in route) / len(route)
        
        # Create map
        m = folium.Map(location=[center_lat, center_lng], zoom_start=14)
        
        # Add route line
        route_coords = [(point.lat, point.lng) for point in route]
        
        # Color the route based on safety scores
        colors = []
        for point in route:
            if point.safety_score >= 80:
                colors.append('green')
            elif point.safety_score >= 60:
                colors.append('yellow')
            elif point.safety_score >= 40:
                colors.append('orange')
            else:
                colors.append('red')
        
        # Draw route segments with different colors
        for i in range(len(route_coords) - 1):
            folium.PolyLine(
                locations=[route_coords[i], route_coords[i + 1]],
                color=colors[i],
                weight=4,
                opacity=0.8,
                popup=f"Safety: {route[i].safety_score:.1f}, Incidents: {route[i].incident_count}"
            ).add_to(m)
        
        # Add start and end markers
        folium.Marker(
            [route[0].lat, route[0].lng],
            popup=f"{start_name}<br>Safety: {route[0].safety_score:.1f}",
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        
        folium.Marker(
            [route[-1].lat, route[-1].lng],
            popup=f"{end_name}<br>Safety: {route[-1].safety_score:.1f}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add incident data as heatmap
        incident_locations = self.incident_data[['Latitude', 'Longitude']].values.tolist()
        HeatMap(
            incident_locations,
            radius=15,
            blur=10,
            max_zoom=13
        ).add_to(m)
        
        return m
    
    def get_route_summary(self, route: List[RoutePoint]) -> Dict:
        """Get a summary of the route safety statistics"""
        if not route:
            return {}
        
        safety_scores = [point.safety_score for point in route]
        incident_counts = [point.incident_count for point in route]
        
        return {
            'total_distance_meters': route[-1].total_distance,
            'num_waypoints': len(route),
            'avg_safety_score': np.mean(safety_scores),
            'min_safety_score': np.min(safety_scores),
            'max_safety_score': np.max(safety_scores),
            'total_incidents_along_route': sum(incident_counts),
            'safety_grade': self._get_safety_grade(np.mean(safety_scores)),
            'route_analysis': {
                'high_safety_segments': len([s for s in safety_scores if s >= 80]),
                'medium_safety_segments': len([s for s in safety_scores if 60 <= s < 80]),
                'low_safety_segments': len([s for s in safety_scores if s < 60])
            }
        }
    
    def _get_safety_grade(self, avg_safety: float) -> str:
        """Convert safety score to letter grade"""
        if avg_safety >= 90:
            return 'A+'
        elif avg_safety >= 80:
            return 'A'
        elif avg_safety >= 70:
            return 'B'
        elif avg_safety >= 60:
            return 'C'
        elif avg_safety >= 50:
            return 'D'
        else:
            return 'F'
    
    def get_safety_recommendations(self, route: List[RoutePoint]) -> List[str]:
        """Get safety recommendations based on the route analysis"""
        recommendations = []
        summary = self.get_route_summary(route)
        
        if summary['avg_safety_score'] < 60:
            recommendations.append("⚠️ This route passes through areas with high incident rates. Consider traveling during daylight hours.")
        
        if summary['route_analysis']['low_safety_segments'] > 0:
            recommendations.append("🚨 Route contains segments with low safety scores. Stay alert and avoid isolated areas.")
        
        if summary['total_incidents_along_route'] > 10:
            recommendations.append("📊 High incident density along route. Consider alternative paths or travel with others.")
        
        if summary['avg_safety_score'] >= 80:
            recommendations.append("✅ This route appears to be relatively safe based on recent incident data.")
        
        # Time-based recommendations
        current_hour = datetime.now().hour
        if current_hour >= 22 or current_hour <= 6:
            recommendations.append("🌙 Night travel detected. Exercise extra caution and stay in well-lit areas.")
        
        return recommendations

# Example usage and demonstration
def main():
    """Demonstrate the SafeRouteFinder with example coordinates in San Francisco"""
    
    # Initialize the route finder
    route_finder = SafeRouteFinder('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')
    
    # Example coordinates in San Francisco
    # Golden Gate Park to Fisherman's Wharf
    start_lat, start_lng = 37.7694, -122.4862  # Golden Gate Park
    end_lat, end_lng = 37.8087, -122.4098      # Fisherman's Wharf
    
    print("=== Safe Route Finder Demo ===")
    print(f"Finding route from Golden Gate Park to Fisherman's Wharf...")
    
    # Find the safest route
    route = route_finder.find_safe_route(start_lat, start_lng, end_lat, end_lng)
    
    if route:
        # Get route summary
        summary = route_finder.get_route_summary(route)
        print("\n=== Route Summary ===")
        for key, value in summary.items():
            if key != 'route_analysis':
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n=== Route Analysis ===")
        for key, value in summary['route_analysis'].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Get safety recommendations
        recommendations = route_finder.get_safety_recommendations(route)
        print("\n=== Safety Recommendations ===")
        for rec in recommendations:
            print(f"• {rec}")
        
        # Create and save the map
        print("\nCreating interactive map...")
        map_obj = route_finder.visualize_route(route, "Golden Gate Park", "Fisherman's Wharf")
        map_obj.save('safe_route_map.html')
        print("Map saved as 'safe_route_map.html'")
        
        # Show some route details
        print("\n=== Route Details ===")
        print(f"Total waypoints: {len(route)}")
        print(f"Total distance: {route[-1].total_distance:.0f} meters")
        print(f"Average safety score: {summary['avg_safety_score']:.1f}")
        print(f"Safety grade: {summary['safety_grade']}")
        
        # Show the 5 most dangerous segments
        dangerous_segments = sorted(route, key=lambda x: x.safety_score)[:5]
        print("\n=== Most Dangerous Segments ===")
        for i, point in enumerate(dangerous_segments, 1):
            print(f"{i}. Lat: {point.lat:.4f}, Lng: {point.lng:.4f}")
            print(f"   Safety Score: {point.safety_score:.1f}, Incidents: {point.incident_count}")
    
    else:
        print("No route found!")

if __name__ == "__main__":
    main() 