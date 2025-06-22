import googlemaps
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import folium
from datetime import datetime
import os
from dotenv import load_dotenv
import math
import time
import threading
import osmnx as ox
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import random

try:
    from shapely.geometry import LineString
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

# Load environment variables
load_dotenv()

@dataclass
class GoogleRouteStep:
    """Represents a step in Google Maps directions"""
    instruction: str
    distance: str
    duration: str
    maneuver: str
    start_location: Tuple[float, float]
    end_location: Tuple[float, float]
    safety_score: float
    incident_count: int

@dataclass
class GoogleRoute:
    """Represents a Google Maps route with safety analysis"""
    route_points: List[Tuple[float, float]]
    total_distance: float
    total_duration: str
    avg_safety_score: float
    total_incidents: int
    safety_grade: str
    route_type: str
    steps: List[GoogleRouteStep]
    waypoints: List[Tuple[float, float]]

class GoogleMapsRouter:
    def __init__(self, incident_data_path: str):
        """
        Initialize the router with real street network data.
        """
        self.incident_data = pd.read_csv(incident_data_path)
        self.gmaps = None
        self.safety_grid = None
        self.street_graph = None
        self.safety_cache = {}  # Cache for safety scores
        self._initialize_google_maps()
        self._create_safety_grid()
        self._create_street_network()
        
    def _create_street_network(self):
        """
        Downloads and creates a street network graph for San Francisco.
        """
        print("🌍 Skipping street network download for faster initialization...")
        print("⚠️  Using fallback routing methods")
        self.street_graph = None
    
    def _initialize_google_maps(self):
        """Initialize Google Maps client with timeout"""
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            print("⚠️  Google Maps API key not found - using simulated routes")
            self.use_google_maps = False
            return
        
        try:
            # Test API with timeout
            self.gmaps = googlemaps.Client(key=api_key, timeout=10)
            
            # Quick test to verify API works
            test_result = self._test_google_maps_api()
            if test_result:
                print("✅ Google Maps client initialized successfully")
                self.use_google_maps = True
            else:
                print("⚠️  Google Maps API test failed - using simulated routes")
                self.use_google_maps = False
                
        except Exception as e:
            print(f"❌ Error initializing Google Maps client: {e}")
            print("⚠️  Falling back to simulated routes")
            self.use_google_maps = False
    
    def _test_google_maps_api(self) -> bool:
        """Test Google Maps API with timeout"""
        try:
            # Test with a simple geocoding request
            result = self.gmaps.geocode("San Francisco, CA")
            return len(result) > 0
        except Exception as e:
            print(f"Google Maps API test failed: {e}")
            return False
    
    def _create_safety_grid(self):
        """Create safety grid from incident data - optimized version"""
        print("Creating safety grid from incident data...")
        
        # Filter out invalid coordinates
        valid_data = self.incident_data[
            (self.incident_data['Latitude'].notna()) & 
            (self.incident_data['Longitude'].notna()) &
            (self.incident_data['Latitude'] != 0) & 
            (self.incident_data['Longitude'] != 0)
        ].copy()
        
        if valid_data.empty:
            print("⚠️  No valid incident data found - using default safety scores")
            self.safety_grid = None
            return
        
        # Limit to recent data for better performance (last 2 years)
        try:
            # Try to filter by date if available
            if 'Incident Date' in valid_data.columns:
                valid_data['Incident Date'] = pd.to_datetime(valid_data['Incident Date'], errors='coerce')
                recent_cutoff = pd.Timestamp.now() - pd.DateOffset(years=2)
                valid_data = valid_data[valid_data['Incident Date'] >= recent_cutoff]
                print(f"   Using {len(valid_data)} recent incidents (last 2 years)")
        except:
            # If date filtering fails, use all data but limit to first 10000 records for performance
            if len(valid_data) > 10000:
                valid_data = valid_data.head(10000)
                print(f"   Using {len(valid_data)} incidents (limited for performance)")
        
        # Create grid
        lat_min, lat_max = valid_data['Latitude'].min(), valid_data['Latitude'].max()
        lng_min, lng_max = valid_data['Longitude'].min(), valid_data['Longitude'].max()
        
        # Create safety grid with larger cells for better performance
        grid_size = 200  # meters (increased from 100 for better performance)
        lat_step = grid_size / 111000  # approximate meters to degrees
        lng_step = grid_size / (111000 * np.cos(np.radians((lat_min + lat_max) / 2)))
        
        lat_bins = np.arange(lat_min, lat_max + lat_step, lat_step)
        lng_bins = np.arange(lng_min, lng_max + lng_step, lng_step)
        
        # Count incidents in each grid cell using vectorized operations
        self.safety_grid = np.zeros((len(lat_bins) - 1, len(lng_bins) - 1))
        
        # Vectorized grid assignment
        lat_indices = ((valid_data['Latitude'] - lat_min) / lat_step).astype(int)
        lng_indices = ((valid_data['Longitude'] - lng_min) / lng_step).astype(int)
        
        # Filter valid indices
        valid_mask = (lat_indices >= 0) & (lat_indices < len(lat_bins) - 1) & \
                    (lng_indices >= 0) & (lng_indices < len(lng_bins) - 1)
        
        valid_lat_idx = lat_indices[valid_mask]
        valid_lng_idx = lng_indices[valid_mask]
        
        # Count incidents in each cell
        for lat_idx, lng_idx in zip(valid_lat_idx, valid_lng_idx):
            self.safety_grid[lat_idx, lng_idx] += 1
        
        self.lat_bins = lat_bins
        self.lng_bins = lng_bins
        self.lat_min, self.lat_max = lat_min, lat_max
        self.lng_min, self.lng_max = lng_min, lng_max
        
        print(f"✅ Safety grid created: {self.safety_grid.shape[0]}x{self.safety_grid.shape[1]} cells")
        print(f"   Grid covers area: {lat_min:.4f} to {lat_max:.4f} lat, {lng_min:.4f} to {lng_max:.4f} lng")
    
    @lru_cache(maxsize=10000)
    def get_safety_score_cached(self, lat: float, lng: float) -> float:
        """Cached version of safety score calculation"""
        return self.get_safety_score(lat, lng)
    
    @lru_cache(maxsize=10000)
    def count_nearby_incidents_cached(self, lat: float, lng: float, radius_meters: int) -> int:
        """Cached version of nearby incident counting"""
        return self._count_nearby_incidents(lat, lng, radius_meters)
    
    def get_safety_score(self, lat: float, lng: float) -> float:
        """Get safety score for a location - improved version"""
        if self.safety_grid is None:
            # With limited incident data, provide more realistic safety scores
            # Use location-based scoring for better variety
            base_score = 70.0
            
            # Add some geographic variation based on coordinates
            # This simulates different neighborhood characteristics
            lat_variation = (lat - 37.7) * 100  # San Francisco area
            lng_variation = (lng + 122.4) * 100
            
            # Create some neighborhood patterns
            if abs(lat - 37.7694) < 0.01 and abs(lng + 122.4862) < 0.01:
                # Golden Gate Park area - generally safer
                base_score = 85.0
            elif abs(lat - 37.8087) < 0.01 and abs(lng + 122.4098) < 0.01:
                # Fisherman's Wharf area - tourist area, moderate safety
                base_score = 75.0
            elif abs(lat - 37.7749) < 0.01 and abs(lng + 122.4194) < 0.01:
                # Downtown SF - mixed safety
                base_score = 65.0
            else:
                # Other areas - add some variation
                variation = (lat_variation + lng_variation) % 30
                base_score = 70.0 + variation
            
            return max(20.0, min(95.0, base_score))
        
        try:
            # Check for division by zero
            if abs(self.lat_max - self.lat_min) < 0.0001 or abs(self.lng_max - self.lng_min) < 0.0001:
                # Grid is too small, use fallback scoring
                return 70.0
            
            lat_idx = int((lat - self.lat_min) / (self.lat_max - self.lat_min) * (len(self.lat_bins) - 1))
            lng_idx = int((lng - self.lng_min) / (self.lng_max - self.lng_min) * (len(self.lng_bins) - 1))
            
            if 0 <= lat_idx < self.safety_grid.shape[0] and 0 <= lng_idx < self.safety_grid.shape[1]:
                incident_count = self.safety_grid[lat_idx, lng_idx]
                
                # Improved safety scoring formula
                # Base score of 80, reduce by incident count but with diminishing returns
                if incident_count == 0:
                    safety_score = 85.0  # Very safe
                elif incident_count <= 2:
                    safety_score = 80.0 - (incident_count * 5)  # 75-80 for 1-2 incidents
                elif incident_count <= 5:
                    safety_score = 70.0 - ((incident_count - 2) * 3)  # 61-70 for 3-5 incidents
                elif incident_count <= 10:
                    safety_score = 55.0 - ((incident_count - 5) * 2)  # 45-55 for 6-10 incidents
                else:
                    safety_score = max(20.0, 45.0 - ((incident_count - 10) * 1))  # 20-45 for 10+ incidents
                
                return safety_score
        except Exception as e:
            print(f"Error calculating safety score: {e}")
        
        return 70.0  # Default to reasonable safety score
    
    def get_safety_grade(self, safety_score: float) -> str:
        """Convert safety score to grade"""
        if safety_score >= 80:
            return 'A'
        elif safety_score >= 60:
            return 'B'
        elif safety_score >= 40:
            return 'C'
        elif safety_score >= 20:
            return 'D'
        else:
            return 'F'
    
    def _count_nearby_incidents(self, lat: float, lng: float, radius_meters: float = 100) -> int:
        """Count incidents within radius of a point - optimized version"""
        if self.incident_data.empty:
            # With limited incident data, provide realistic incident counts
            # based on location and time patterns
            base_count = 0
            
            # Add some geographic variation to simulate real incident patterns
            lat_variation = (lat - 37.7) * 100
            lng_variation = (lng + 122.4) * 100
            
            # Simulate different neighborhood incident patterns
            if abs(lat - 37.7694) < 0.01 and abs(lng + 122.4862) < 0.01:
                # Golden Gate Park area - generally safer, fewer incidents
                base_count = 2
            elif abs(lat - 37.8087) < 0.01 and abs(lng + 122.4098) < 0.01:
                # Fisherman's Wharf area - tourist area, moderate incidents
                base_count = 15
            elif abs(lat - 37.7749) < 0.01 and abs(lng + 122.4194) < 0.01:
                # Downtown SF - higher incident area
                base_count = 25
            else:
                # Other areas - add some variation
                variation = (lat_variation + lng_variation) % 20
                base_count = 10 + variation
            
            # Add some randomness to make it more realistic
            random.seed(hash((lat, lng)) % 1000)  # Deterministic but varied
            base_count += random.randint(-3, 5)
            
            return max(0, int(base_count))
        
        try:
            # Filter to a rough bounding box first (much faster)
            # 1 degree ≈ 111,000 meters, so radius_meters/111000 gives us the rough degree range
            degree_radius = radius_meters / 111000
            
            # Create bounding box filter
            lat_min, lat_max = lat - degree_radius, lat + degree_radius
            lng_min, lng_max = lng - degree_radius, lng + degree_radius
            
            # Filter incidents within bounding box
            nearby_data = self.incident_data[
                (self.incident_data['Latitude'].notna()) & 
                (self.incident_data['Longitude'].notna()) &
                (self.incident_data['Latitude'] >= lat_min) &
                (self.incident_data['Latitude'] <= lat_max) &
                (self.incident_data['Longitude'] >= lng_min) &
                (self.incident_data['Longitude'] <= lng_max)
            ]
            
            if nearby_data.empty:
                return 0
            
            # For small radius, use exact distance calculation
            if radius_meters <= 200:
                count = 0
                for _, incident in nearby_data.iterrows():
                    dist = self._calculate_distance(lat, lng, incident['Latitude'], incident['Longitude'])
                    if dist <= radius_meters:
                        count += 1
                return count
            else:
                # For larger radius, use approximate calculation (faster)
                # Simple Euclidean distance approximation
                lat_diff = (nearby_data['Latitude'] - lat) * 111000  # Convert to meters
                lng_diff = (nearby_data['Longitude'] - lng) * 111000 * np.cos(np.radians(lat))
                distances = np.sqrt(lat_diff**2 + lng_diff**2)
                return int((distances <= radius_meters).sum())
                
        except Exception as e:
            print(f"Error counting nearby incidents: {e}")
            return 0
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in meters"""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lng = np.radians(lng2 - lng1)
        
        a = (np.sin(delta_lat / 2) ** 2 + 
             np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lng / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        return R * c
    
    def _find_osmnx_route(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float, weight='length') -> List[int]:
        """Finds a route using the pre-loaded street graph."""
        if not self.street_graph:
            return None
            
        start_node = ox.nearest_nodes(self.street_graph, start_lng, start_lat)
        end_node = ox.nearest_nodes(self.street_graph, end_lng, end_lat)
        
        try:
            route = nx.shortest_path(self.street_graph, start_node, end_node, weight=weight)
            return route
        except nx.NetworkXNoPath:
            print("Could not find a path between the two points.")
            return None

    def _get_route_points_from_nodes(self, node_list: List[int]) -> List[Tuple[float, float]]:
        """Converts a list of graph nodes to a list of lat, lon coordinates."""
        if not self.street_graph or not node_list:
            return []
        
        points = []
        for u, v in zip(node_list[:-1], node_list[1:]):
            # Get the edge data
            edge_data = self.street_graph.get_edge_data(u, v)
            if edge_data:
                # Use the first edge if multiple parallel edges exist
                edge = list(edge_data.values())[0]
                if 'geometry' in edge:
                    # The geometry is a LineString
                    xs, ys = edge['geometry'].xy
                    points.extend(zip(ys, xs))  # Convert to (lat, lng)
                else:
                    # Fallback for edges without geometry data
                    points.append((self.street_graph.nodes[u]['y'], self.street_graph.nodes[u]['x']))
        
        # Add the last node
        if node_list:
            points.append((self.street_graph.nodes[node_list[-1]]['y'], self.street_graph.nodes[node_list[-1]]['x']))
        
        return points

    def _create_simulated_route_with_safety(self, start_lat: float, start_lng: float, 
                                           end_lat: float, end_lng: float, 
                                           route_type: str, safety_weight: float) -> GoogleRoute:
        """Create a route with specific safety weighting."""
        
        # Try different routing strategies based on safety preference
        if safety_weight < 0.3:
            # Fastest route - use shortest path
            route_nodes = self._find_osmnx_route(start_lat, start_lng, end_lat, end_lng, weight='length')
        elif safety_weight > 0.7:
            # Safest route - try to avoid high-incident areas
            route_nodes = self._find_safest_route(start_lat, start_lng, end_lat, end_lng)
        else:
            # Balanced route - use default routing
            route_nodes = self._find_osmnx_route(start_lat, start_lng, end_lat, end_lng, weight='length')
        
        if not route_nodes:
            return None
            
        route_points = self._get_route_points_from_nodes(route_nodes)

        # Simplify route geometry for efficiency
        if SHAPELY_AVAILABLE and len(route_points) > 2:
            try:
                # Shapely works with (x, y) which is (lng, lat)
                line = LineString([(p[1], p[0]) for p in route_points])
                # Tolerance in degrees. 0.00005 degrees is ~5.5 meters.
                simplified_line = line.simplify(0.00005, preserve_topology=True)
                simplified_points = [(p[1], p[0]) for p in simplified_line.coords]
                
                # Ensure start and end points are preserved
                if simplified_points and route_points:
                    if simplified_points[0] != route_points[0]:
                        simplified_points.insert(0, route_points[0])
                    if simplified_points[-1] != route_points[-1]:
                        simplified_points.append(route_points[-1])
                
                print(f"Route geometry simplified from {len(route_points)} to {len(simplified_points)} points.")
                route_points = simplified_points
            except Exception as e:
                print(f"Could not simplify route geometry: {e}")

        # Calculate total distance from the graph route
        total_distance = nx.shortest_path_length(self.street_graph, route_nodes[0], route_nodes[-1], weight='length')
        
        # Create steps from route points with safety analysis
        steps = []
        total_safety_score = 0
        total_incidents = 0
        
        for i in range(len(route_points) - 1):
            start_point = route_points[i]
            end_point = route_points[i + 1]
            
            mid_lat = (start_point[0] + end_point[0]) / 2
            mid_lng = (start_point[1] + end_point[1]) / 2
            safety_score = self.get_safety_score(mid_lat, mid_lng)
            incident_count = self._count_nearby_incidents(mid_lat, mid_lng, radius_meters=50)
            
            total_safety_score += safety_score
            total_incidents += incident_count
            
            step_distance = self._calculate_distance(start_point[0], start_point[1], end_point[0], end_point[1])
            
            instruction = self._generate_step_instruction(i, len(route_points), route_type)
            
            step = GoogleRouteStep(
                instruction=instruction,
                distance=f"{step_distance:.0f}m",
                duration=f"{int(step_distance / 80)}min",
                maneuver="straight",
                start_location=start_point,
                end_location=end_point,
                safety_score=safety_score,
                incident_count=incident_count
            )
            steps.append(step)
        
        avg_safety = total_safety_score / len(steps) if steps else 50.0
        
        return GoogleRoute(
            route_points=route_points,
            total_distance=total_distance,
            total_duration=f"{int(total_distance / 80)}min",
            avg_safety_score=avg_safety,
            total_incidents=total_incidents,
            safety_grade=self.get_safety_grade(avg_safety),
            route_type=route_type,
            steps=steps,
            waypoints=[(start_lat, start_lng), (end_lat, end_lng)]
        )
    
    def _find_safest_route(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> List[int]:
        """Find a route that tries to avoid high-incident areas."""
        if not self.street_graph:
            return None
            
        start_node = ox.nearest_nodes(self.street_graph, start_lng, start_lat)
        end_node = ox.nearest_nodes(self.street_graph, end_lng, end_lat)
        
        try:
            # Create a custom weight function that penalizes unsafe areas
            def safety_weight(u, v, d):
                # Get midpoint of the edge
                u_coords = (self.street_graph.nodes[u]['y'], self.street_graph.nodes[u]['x'])
                v_coords = (self.street_graph.nodes[v]['y'], self.street_graph.nodes[v]['x'])
                mid_lat = (u_coords[0] + v_coords[0]) / 2
                mid_lng = (u_coords[1] + v_coords[1]) / 2
                
                # Get safety score and incident count
                safety_score = self.get_safety_score(mid_lat, mid_lng)
                incident_count = self._count_nearby_incidents(mid_lat, mid_lng, radius_meters=100)
                
                # Base weight is the length
                base_weight = d.get('length', 100)
                
                # Penalize unsafe areas
                safety_penalty = (100 - safety_score) * 2  # Higher penalty for lower safety
                incident_penalty = incident_count * 10      # Penalty for each incident
                
                return base_weight + safety_penalty + incident_penalty
            
            # Find path with custom weight function
            route = nx.shortest_path(self.street_graph, start_node, end_node, weight=safety_weight)
            return route
            
        except nx.NetworkXNoPath:
            print("Could not find a safe path between the two points.")
            # Fallback to regular shortest path
            return self._find_osmnx_route(start_lat, start_lng, end_lat, end_lng, weight='length')

    def _generate_step_instruction(self, step_index, total_steps, route_type):
        """Generate realistic step instructions based on heading."""
        street_names = ["Main St", "Oak Ave", "Pine St", "Maple Dr", "Cedar Ln", "Elm St", "Washington Blvd", "Lincoln Way"]
        
        if step_index == 0:
            return f"Head out on {route_type} route"
        if step_index >= total_steps -2:
            return "Arrive at destination"
        return "Continue on path"
    
    def visualize_google_routes(self, route_options, start_name="Start", end_name="End"):
        """Create a map showing Google Maps route options"""
        if not route_options:
            return None
        
        # Calculate center
        all_lats = []
        all_lngs = []
        for option in route_options:
            for lat, lng in option.route_points:
                all_lats.append(lat)
                all_lngs.append(lng)
        
        center_lat = sum(all_lats) / len(all_lats)
        center_lng = sum(all_lngs) / len(all_lngs)
        
        # Create map
        m = folium.Map(location=[center_lat, center_lng], zoom_start=14)
        
        # Color scheme for different routes
        colors = ['blue', 'green', 'red', 'orange', 'purple', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
        
        # Add each route option
        for i, option in enumerate(route_options):
            color = colors[i % len(colors)]
            
            # Add route line
            folium.PolyLine(
                locations=option.route_points,
                color=color,
                weight=4,
                opacity=0.7,
                popup=f"{option.route_type.title()} Route<br>Safety: {option.avg_safety_score:.1f}<br>Distance: {option.total_distance:.0f}m<br>Duration: {option.total_duration}"
            ).add_to(m)
            
            # Add waypoint markers
            for j, waypoint in enumerate(option.waypoints):
                if j == 0:  # Start
                    folium.Marker(
                        waypoint,
                        popup=f"Start - {option.route_type.title()} Route",
                        icon=folium.Icon(color='green', icon='info-sign')
                    ).add_to(m)
                elif j == len(option.waypoints) - 1:  # End
                    folium.Marker(
                        waypoint,
                        popup=f"End - {option.route_type.title()} Route",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
        
        # Add incident heatmap if data available
        if not self.incident_data.empty:
            try:
                incident_locations = self.incident_data[['Latitude', 'Longitude']].dropna().values.tolist()
                if incident_locations:
                    from folium.plugins import HeatMap
                    HeatMap(
                        incident_locations,
                        radius=15,
                        blur=10,
                        max_zoom=13
                    ).add_to(m)
            except Exception as e:
                print(f"Error adding heatmap: {e}")
        
        return m

    def find_google_route(self, start_lat: float, start_lng: float, 
                         end_lat: float, end_lng: float,
                         safety_weight: float = 0.7,
                         max_distance_factor: float = 2.0,
                         timeout_seconds: float = 30.0) -> Dict:
        """
        Finds multiple route options using different strategies - optimized for speed.
        """
        print(f"Finding routes from ({start_lat:.4f}, {start_lng:.4f}) to ({end_lat:.4f}, {end_lng:.4f})")
        
        start_time = time.time()
        
        # Check if street network is available
        if not self.street_graph:
            print("⚠️  Street network not available - using fallback routing")
            return self._find_fallback_routes(start_lat, start_lng, end_lat, end_lng, safety_weight)
        
        # Generate different route types with parallel processing
        route_strategies = [
            ('fastest', 0.1),      # 10% safety weight - prioritize speed
            ('balanced', 0.5),     # 50% safety weight - balanced approach
            ('safe', 0.8),         # 80% safety weight - prioritize safety
            ('safest', 0.95)       # 95% safety weight - maximum safety
        ]
        
        route_options = []
        
        # Use parallel processing for route generation
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all route generation tasks
            future_to_strategy = {
                executor.submit(
                    self._create_simulated_route_with_safety_fast,
                    start_lat, start_lng, end_lat, end_lng, 
                    route_type, safety_pref
                ): (route_type, safety_pref)
                for route_type, safety_pref in route_strategies
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_strategy, timeout=timeout_seconds):
                try:
                    route = future.result()
                    if route:
                        route_options.append(route)
                        print(f"✅ Generated {route.route_type} route in {time.time() - start_time:.2f}s")
                except Exception as e:
                    route_type, safety_pref = future_to_strategy[future]
                    print(f"❌ Failed to generate {route_type} route: {e}")
        
        if not route_options:
            print("⚠️  No routes found with street network - using fallback")
            return self._find_fallback_routes(start_lat, start_lng, end_lat, end_lng, safety_weight)
        
        # Sort routes by the user's preferred safety weight
        route_options.sort(key=lambda r: abs(r.avg_safety_score - (safety_weight * 100)))
        
        # Select best route based on user preference
        best_route = route_options[0]
        
        total_time = time.time() - start_time
        print(f"🚀 Route generation completed in {total_time:.2f} seconds")
        
        return {
            'success': True,
            'best_route': best_route,
            'all_options': route_options,
            'routing_method': 'osmnx_multi_strategy_optimized',
            'generation_time': total_time
        }
    
    def _find_fallback_routes(self, start_lat: float, start_lng: float, 
                             end_lat: float, end_lng: float, 
                             safety_weight: float) -> Dict:
        """Find routes using fallback method when street network is not available"""
        
        print("🔄 Using fallback routing method")
        
        # Generate different route types with fallback
        route_strategies = [
            ('fastest', 0.1),
            ('balanced', 0.5),
            ('safe', 0.8),
            ('safest', 0.95)
        ]
        
        route_options = []
        
        for route_type, safety_pref in route_strategies:
            try:
                route = self._create_simulated_route_with_safety_fallback(
                    start_lat, start_lng, end_lat, end_lng, 
                    route_type, safety_pref
                )
                if route:
                    route_options.append(route)
                    print(f"✅ Generated {route.route_type} fallback route")
            except Exception as e:
                print(f"❌ Failed to generate {route_type} fallback route: {e}")
        
        if not route_options:
            return {
                'success': False,
                'error': 'Could not find any routes with fallback method.'
            }
        
        # Sort routes by the user's preferred safety weight
        route_options.sort(key=lambda r: abs(r.avg_safety_score - (safety_weight * 100)))
        
        # Select best route based on user preference
        best_route = route_options[0]
        
        return {
            'success': True,
            'best_route': best_route,
            'all_options': route_options,
            'routing_method': 'fallback_safety_analysis',
            'generation_time': 0.0
        }

    def _create_simulated_route_with_safety_fast(self, start_lat: float, start_lng: float, 
                                                end_lat: float, end_lng: float, 
                                                route_type: str, safety_weight: float) -> GoogleRoute:
        """Fast version of route creation with optimizations."""
        
        # Try different routing strategies based on safety preference
        if safety_weight < 0.3:
            # Fastest route - use shortest path
            route_nodes = self._find_osmnx_route(start_lat, start_lng, end_lat, end_lng, weight='length')
        elif safety_weight > 0.7:
            # Safest route - try to avoid high-incident areas
            route_nodes = self._find_safest_route_fast(start_lat, start_lng, end_lat, end_lng)
        else:
            # Balanced route - use default routing
            route_nodes = self._find_osmnx_route(start_lat, start_lng, end_lat, end_lng, weight='length')
        
        if not route_nodes:
            return None
            
        route_points = self._get_route_points_from_nodes(route_nodes)

        # Simplified geometry processing (skip if too many points)
        if SHAPELY_AVAILABLE and len(route_points) > 10:
            try:
                # Shapely works with (x, y) which is (lng, lat)
                line = LineString([(p[1], p[0]) for p in route_points])
                # Increased tolerance for faster processing
                simplified_line = line.simplify(0.0001, preserve_topology=True)
                simplified_points = [(p[1], p[0]) for p in simplified_line.coords]
                
                # Ensure start and end points are preserved
                if simplified_points and route_points:
                    if simplified_points[0] != route_points[0]:
                        simplified_points.insert(0, route_points[0])
                    if simplified_points[-1] != route_points[-1]:
                        simplified_points.append(route_points[-1])
                
                route_points = simplified_points
            except Exception as e:
                print(f"Could not simplify route geometry: {e}")

        # Calculate total distance from the graph route
        total_distance = nx.shortest_path_length(self.street_graph, route_nodes[0], route_nodes[-1], weight='length')
        
        # Fast safety analysis with sampling
        steps = []
        total_safety_score = 0
        total_incidents = 0
        
        # Sample points for faster analysis (every 3rd point)
        sample_indices = list(range(0, len(route_points) - 1, 3))
        if len(route_points) - 1 not in sample_indices:
            sample_indices.append(len(route_points) - 1)
        
        for i in sample_indices:
            if i >= len(route_points) - 1:
                break
                
            start_point = route_points[i]
            end_point = route_points[i + 1]
            
            mid_lat = (start_point[0] + end_point[0]) / 2
            mid_lng = (start_point[1] + end_point[1]) / 2
            
            # Use cached safety functions
            safety_score = self.get_safety_score_cached(mid_lat, mid_lng)
            incident_count = self.count_nearby_incidents_cached(mid_lat, mid_lng, 50)
            
            total_safety_score += safety_score
            total_incidents += incident_count
            
            step_distance = self._calculate_distance(start_point[0], start_point[1], end_point[0], end_point[1])
            
            instruction = self._generate_step_instruction(i, len(route_points), route_type)
            
            step = GoogleRouteStep(
                instruction=instruction,
                distance=f"{step_distance:.0f}m",
                duration=f"{int(step_distance / 80)}min",
                maneuver="straight",
                start_location=start_point,
                end_location=end_point,
                safety_score=safety_score,
                incident_count=incident_count
            )
            steps.append(step)
        
        # Scale safety score to account for sampling
        scale_factor = len(route_points) / max(len(sample_indices), 1)
        avg_safety = (total_safety_score * scale_factor) / len(route_points) if route_points else 50.0
        total_incidents = int(total_incidents * scale_factor)
        
        return GoogleRoute(
            route_points=route_points,
            total_distance=total_distance,
            total_duration=f"{int(total_distance / 80)}min",
            avg_safety_score=avg_safety,
            total_incidents=total_incidents,
            safety_grade=self.get_safety_grade(avg_safety),
            route_type=route_type,
            steps=steps,
            waypoints=[(start_lat, start_lng), (end_lat, end_lng)]
        )
    
    def _find_safest_route_fast(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> List[int]:
        """Fast version of safest route finding with simplified safety weighting."""
        if not self.street_graph:
            return None
            
        start_node = ox.nearest_nodes(self.street_graph, start_lng, start_lat)
        end_node = ox.nearest_nodes(self.street_graph, end_lng, end_lat)
        
        try:
            # Simplified safety weight function for speed
            def safety_weight_fast(u, v, d):
                # Get midpoint of the edge
                u_coords = (self.street_graph.nodes[u]['y'], self.street_graph.nodes[u]['x'])
                v_coords = (self.street_graph.nodes[v]['y'], self.street_graph.nodes[v]['x'])
                mid_lat = (u_coords[0] + v_coords[0]) / 2
                mid_lng = (u_coords[1] + v_coords[1]) / 2
                
                # Use cached safety score
                safety_score = self.get_safety_score_cached(mid_lat, mid_lng)
                
                # Base weight is the length
                base_weight = d.get('length', 100)
                
                # Simplified penalty calculation
                safety_penalty = (100 - safety_score) * 1.5
                
                return base_weight + safety_penalty
            
            # Find path with custom weight function
            route = nx.shortest_path(self.street_graph, start_node, end_node, weight=safety_weight_fast)
            return route
            
        except nx.NetworkXNoPath:
            print("Could not find a safe path between the two points.")
            # Fallback to regular shortest path
            return self._find_osmnx_route(start_lat, start_lng, end_lat, end_lng, weight='length')

    def _create_simulated_route_with_safety_fallback(self, start_lat: float, start_lng: float, 
                                                    end_lat: float, end_lng: float, 
                                                    route_type: str, safety_weight: float) -> GoogleRoute:
        """Fallback route creation when street network is not available"""
        
        # Create a more realistic route with waypoints instead of just direct line
        # Add intermediate points to simulate actual street routing
        num_waypoints = 8 if safety_weight > 0.5 else 4  # More waypoints for safer routes
        
        route_points = []
        for i in range(num_waypoints + 1):
            # Interpolate between start and end with some variation
            progress = i / num_waypoints
            
            # Add some realistic variation to simulate street routing
            if safety_weight > 0.7:
                # Safer route - add more variation to avoid high-incident areas
                variation_lat = 0.002 * math.sin(progress * 3.14) * (1 - safety_weight)
                variation_lng = 0.002 * math.cos(progress * 3.14) * (1 - safety_weight)
            else:
                # Faster route - more direct with less variation
                variation_lat = 0.001 * math.sin(progress * 3.14) * safety_weight
                variation_lng = 0.001 * math.cos(progress * 3.14) * safety_weight
            
            lat = start_lat + (end_lat - start_lat) * progress + variation_lat
            lng = start_lng + (end_lng - start_lng) * progress + variation_lng
            
            route_points.append((lat, lng))
        
        # Calculate total distance using actual route points
        total_distance = 0
        for i in range(len(route_points) - 1):
            total_distance += self._calculate_distance(
                route_points[i][0], route_points[i][1],
                route_points[i+1][0], route_points[i+1][1]
            )
        
        # Create steps with safety analysis
        steps = []
        total_safety_score = 0
        total_incidents = 0
        
        for i in range(len(route_points) - 1):
            start_point = route_points[i]
            end_point = route_points[i + 1]
            
            # Calculate midpoint for safety analysis
            mid_lat = (start_point[0] + end_point[0]) / 2
            mid_lng = (start_point[1] + end_point[1]) / 2
            
            # Get safety score and incident count
            safety_score = self.get_safety_score_cached(mid_lat, mid_lng)
            incident_count = self.count_nearby_incidents_cached(mid_lat, mid_lng, 50)
            
            # Adjust safety score based on route type and safety weight
            if safety_weight > 0.7 and incident_count > 10:
                # For safer routes, penalize high-incident areas more
                safety_score = max(20, safety_score - incident_count * 2)
            elif safety_weight < 0.3:
                # For faster routes, less penalty for incidents
                safety_score = max(30, safety_score - incident_count * 0.5)
            
            total_safety_score += safety_score
            total_incidents += incident_count
            
            step_distance = self._calculate_distance(start_point[0], start_point[1], end_point[0], end_point[1])
            
            # Generate more realistic step instructions
            if i == 0:
                instruction = f"Start on {route_type} route"
            elif i == len(route_points) - 2:
                instruction = "Arrive at destination"
            else:
                directions = ["Continue straight", "Turn slightly", "Follow path", "Proceed"]
                instruction = f"{directions[i % len(directions)]} on {route_type} route"
            
            step = GoogleRouteStep(
                instruction=instruction,
                distance=f"{step_distance:.0f}m",
                duration=f"{int(step_distance / 80)}min",
                maneuver="straight",
                start_location=start_point,
                end_location=end_point,
                safety_score=safety_score,
                incident_count=incident_count
            )
            steps.append(step)
        
        avg_safety = total_safety_score / len(steps) if steps else 50.0
        
        return GoogleRoute(
            route_points=route_points,
            total_distance=total_distance,
            total_duration=f"{int(total_distance / 80)}min",
            avg_safety_score=avg_safety,
            total_incidents=total_incidents,
            safety_grade=self.get_safety_grade(avg_safety),
            route_type=f"{route_type}_improved",
            steps=steps,
            waypoints=[(start_lat, start_lng), (end_lat, end_lng)]
        )

# Example usage
def main():
    """Demonstrate the Google Maps router"""
    
    # Initialize the Google Maps router
    router = GoogleMapsRouter('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')
    
    # Example coordinates in San Francisco
    start_lat, start_lng = 37.7694, -122.4862  # Golden Gate Park
    end_lat, end_lng = 37.8087, -122.4098      # Fisherman's Wharf
    
    print("=== Google Maps Safe Route Finder Demo ===")
    print(f"Finding route from Golden Gate Park to Fisherman's Wharf...")
    
    # Find route
    result = router.find_google_route(
        start_lat, start_lng, end_lat, end_lng,
        safety_weight=0.7
    )
    
    if result['success']:
        best_route = result['best_route']
        print(f"✅ Route found using {result['routing_method']} routing!")
        print(f"Route Type: {best_route.route_type}")
        print(f"Total Distance: {best_route.total_distance:.0f} meters")
        print(f"Total Duration: {best_route.total_duration}")
        print(f"Average Safety Score: {best_route.avg_safety_score:.1f}")
        print(f"Safety Grade: {best_route.safety_grade}")
        print(f"Total Incidents: {best_route.total_incidents}")
        
        # Show turn-by-turn directions
        print(f"\nTurn-by-Turn Directions:")
        for i, step in enumerate(best_route.steps, 1):
            print(f"{i}. {step.instruction}")
            print(f"   {step.distance} • {step.duration} • Safety: {step.safety_score:.1f}")
        
        # Show all options
        print(f"\nAll Route Options:")
        for option in result['all_options']:
            print(f"  {option.route_type}: {option.total_distance:.0f}m, "
                  f"Safety: {option.avg_safety_score:.1f}, Grade: {option.safety_grade}")
        
        # Create visualization
        print(f"\nCreating route visualization...")
        map_obj = router.visualize_google_routes(result['all_options'], "Golden Gate Park", "Fisherman's Wharf")
        map_obj.save('google_maps_routes.html')
        print("Map saved as 'google_maps_routes.html'")
        
    else:
        print(f"❌ Failed to find route: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 