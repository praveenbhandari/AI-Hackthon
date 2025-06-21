import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import folium
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

@dataclass
class RoadRoute:
    """Represents a road-aware route with safety analysis"""
    route_points: List[Tuple[float, float]]
    total_distance: float
    avg_safety_score: float
    total_incidents: int
    safety_grade: str
    route_type: str
    waypoints: List[Tuple[float, float]]
    road_segments: List[Dict]

class RoadAwareRouter:
    def __init__(self, incident_data_path: str, city: str = "San Francisco, CA, USA"):
        """
        Initialize the road-aware router
        
        Args:
            incident_data_path: Path to police incident data CSV
            city: City name for OpenStreetMap data
        """
        self.city = city
        self.incident_data = pd.read_csv(incident_data_path)
        self.graph = None
        self.safety_grid = None
        self._load_road_network()
        self._create_safety_grid()
        
    def _load_road_network(self):
        """Load road network from OpenStreetMap"""
        print(f"Loading road network for {self.city}...")
        
        try:
            # Download and create the graph
            self.graph = ox.graph_from_place(self.city, network_type='walk')
            
            # Project to local coordinate system for accurate distance calculations
            self.graph = ox.project_graph(self.graph)
            
            print(f"✅ Road network loaded: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")
            
        except Exception as e:
            print(f"❌ Error loading road network: {e}")
            print("Falling back to basic routing...")
            self.graph = None
    
    def _create_safety_grid(self):
        """Create safety grid from incident data"""
        print("Creating safety grid from incident data...")
        
        # Filter out invalid coordinates
        valid_data = self.incident_data[
            (self.incident_data['Latitude'].notna()) & 
            (self.incident_data['Longitude'].notna()) &
            (self.incident_data['Latitude'] != 0) & 
            (self.incident_data['Longitude'] != 0)
        ].copy()
        
        # Create grid
        lat_min, lat_max = valid_data['Latitude'].min(), valid_data['Latitude'].max()
        lng_min, lng_max = valid_data['Longitude'].min(), valid_data['Longitude'].max()
        
        # Create safety grid
        grid_size = 100  # meters
        lat_step = grid_size / 111000  # approximate meters to degrees
        lng_step = grid_size / (111000 * np.cos(np.radians((lat_min + lat_max) / 2)))
        
        lat_bins = np.arange(lat_min, lat_max + lat_step, lat_step)
        lng_bins = np.arange(lng_min, lng_max + lng_step, lng_step)
        
        # Count incidents in each grid cell
        self.safety_grid = np.zeros((len(lat_bins) - 1, len(lng_bins) - 1))
        
        for _, incident in valid_data.iterrows():
            lat_idx = int((incident['Latitude'] - lat_min) / lat_step)
            lng_idx = int((incident['Longitude'] - lng_min) / lng_step)
            
            if 0 <= lat_idx < len(lat_bins) - 1 and 0 <= lng_idx < len(lng_bins) - 1:
                self.safety_grid[lat_idx, lng_idx] += 1
        
        self.lat_bins = lat_bins
        self.lng_bins = lng_bins
        self.lat_min, self.lat_max = lat_min, lat_max
        self.lng_min, self.lng_max = lng_min, lng_max
        
        print(f"✅ Safety grid created: {self.safety_grid.shape[0]}x{self.safety_grid.shape[1]} cells")
    
    def get_safety_score(self, lat: float, lng: float) -> float:
        """Get safety score for a location"""
        if self.safety_grid is None:
            return 50.0
        
        lat_idx = int((lat - self.lat_min) / (self.lat_max - self.lat_min) * (len(self.lat_bins) - 1))
        lng_idx = int((lng - self.lng_min) / (self.lng_max - self.lng_min) * (len(self.lng_bins) - 1))
        
        if 0 <= lat_idx < self.safety_grid.shape[0] and 0 <= lng_idx < self.safety_grid.shape[1]:
            incident_count = self.safety_grid[lat_idx, lng_idx]
            # Convert incident count to safety score (0-100, higher is safer)
            safety_score = max(0, 100 - (incident_count * 10))
            return safety_score
        
        return 50.0
    
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
    
    def find_nearest_node(self, lat: float, lng: float) -> int:
        """Find the nearest road network node to given coordinates"""
        if self.graph is None:
            return None
        
        # Get the nearest node to the coordinates
        nearest_node = ox.nearest_nodes(self.graph, lng, lat)
        return nearest_node
    
    def find_road_route(self, start_lat: float, start_lng: float, 
                       end_lat: float, end_lng: float,
                       safety_weight: float = 0.7,
                       max_distance_factor: float = 2.0) -> Dict:
        """
        Find road-aware safe route
        
        Args:
            start_lat, start_lng: Starting coordinates
            end_lat, end_lng: Ending coordinates
            safety_weight: Weight given to safety vs distance (0-1)
            max_distance_factor: Maximum route length as factor of direct distance
        
        Returns:
            Dictionary with route information
        """
        print(f"Finding road-aware route from ({start_lat:.4f}, {start_lng:.4f}) to ({end_lat:.4f}, {end_lng:.4f})")
        
        if self.graph is None:
            return self._fallback_route(start_lat, start_lng, end_lat, end_lng, safety_weight)
        
        # Find nearest nodes
        start_node = self.find_nearest_node(start_lat, start_lng)
        end_node = self.find_nearest_node(end_lat, end_lng)
        
        if start_node is None or end_node is None:
            print("Could not find nearest road nodes, using fallback routing")
            return self._fallback_route(start_lat, start_lng, end_lat, end_lng, safety_weight)
        
        # Generate multiple route options
        route_options = self._generate_road_route_options(
            start_node, end_node, start_lat, start_lng, end_lat, end_lng,
            safety_weight, max_distance_factor
        )
        
        if not route_options:
            return self._fallback_route(start_lat, start_lng, end_lat, end_lng, safety_weight)
        
        # Select best route
        best_route = self._select_best_road_route(route_options, safety_weight)
        
        return {
            'success': True,
            'best_route': best_route,
            'all_options': route_options,
            'routing_method': 'road_aware'
        }
    
    def _generate_road_route_options(self, start_node: int, end_node: int,
                                   start_lat: float, start_lng: float,
                                   end_lat: float, end_lng: float,
                                   safety_weight: float, max_distance_factor: float) -> List[RoadRoute]:
        """Generate multiple road-aware route options"""
        options = []
        
        # Calculate direct distance
        direct_distance = self._calculate_distance(start_lat, start_lng, end_lat, end_lng)
        max_distance = direct_distance * max_distance_factor
        
        # Option 1: Shortest path (fastest)
        shortest_route = self._create_shortest_path_route(start_node, end_node, start_lat, start_lng, end_lat, end_lng)
        if shortest_route:
            options.append(shortest_route)
        
        # Option 2: Safety-optimized path
        safe_route = self._create_safety_optimized_route(start_node, end_node, start_lat, start_lng, end_lat, end_lng, max_distance)
        if safe_route:
            options.append(safe_route)
        
        # Option 3: Balanced path
        balanced_route = self._create_balanced_route(start_node, end_node, start_lat, start_lng, end_lat, end_lng, max_distance)
        if balanced_route:
            options.append(balanced_route)
        
        # Option 4: Scenic path (avoids main roads)
        scenic_route = self._create_scenic_route(start_node, end_node, start_lat, start_lng, end_lat, end_lng, max_distance)
        if scenic_route:
            options.append(scenic_route)
        
        return options
    
    def _create_shortest_path_route(self, start_node: int, end_node: int,
                                  start_lat: float, start_lng: float,
                                  end_lat: float, end_lng: float) -> Optional[RoadRoute]:
        """Create shortest path route"""
        try:
            # Find shortest path
            path = nx.shortest_path(self.graph, start_node, end_node, weight='length')
            
            # Get route coordinates
            route_coords = []
            for node in path:
                node_data = self.graph.nodes[node]
                route_coords.append((node_data['y'], node_data['x']))  # lat, lng
            
            # Calculate route metrics
            total_distance = sum(
                self._calculate_distance(route_coords[i][0], route_coords[i][1],
                                       route_coords[i+1][0], route_coords[i+1][1])
                for i in range(len(route_coords) - 1)
            )
            
            # Calculate safety metrics
            safety_scores = [self.get_safety_score(lat, lng) for lat, lng in route_coords]
            avg_safety = np.mean(safety_scores)
            
            # Count incidents along route
            total_incidents = sum(
                self._count_nearby_incidents(lat, lng, radius_meters=100)
                for lat, lng in route_coords
            )
            
            return RoadRoute(
                route_points=route_coords,
                total_distance=total_distance,
                avg_safety_score=avg_safety,
                total_incidents=total_incidents,
                safety_grade=self.get_safety_grade(avg_safety),
                route_type='shortest',
                waypoints=[(start_lat, start_lng), (end_lat, end_lng)],
                road_segments=self._get_road_segments(path)
            )
            
        except Exception as e:
            print(f"Error creating shortest path route: {e}")
            return None
    
    def _create_safety_optimized_route(self, start_node: int, end_node: int,
                                     start_lat: float, start_lng: float,
                                     end_lat: float, end_lng: float,
                                     max_distance: float) -> Optional[RoadRoute]:
        """Create safety-optimized route"""
        try:
            # Use A* with safety-weighted cost
            def safety_cost(u, v, d):
                # Get coordinates of the edge
                u_coords = (self.graph.nodes[u]['y'], self.graph.nodes[u]['x'])
                v_coords = (self.graph.nodes[v]['y'], self.graph.nodes[v]['x'])
                
                # Calculate safety score for this segment
                mid_lat = (u_coords[0] + v_coords[0]) / 2
                mid_lng = (u_coords[1] + v_coords[1]) / 2
                safety_score = self.get_safety_score(mid_lat, mid_lng)
                
                # Weight the cost based on safety (lower safety = higher cost)
                safety_factor = 1 + (100 - safety_score) / 100
                return d['length'] * safety_factor
            
            path = nx.astar_path(self.graph, start_node, end_node, weight=safety_cost)
            
            # Get route coordinates and calculate metrics
            route_coords = []
            for node in path:
                node_data = self.graph.nodes[node]
                route_coords.append((node_data['y'], node_data['x']))
            
            total_distance = sum(
                self._calculate_distance(route_coords[i][0], route_coords[i][1],
                                       route_coords[i+1][0], route_coords[i+1][1])
                for i in range(len(route_coords) - 1)
            )
            
            safety_scores = [self.get_safety_score(lat, lng) for lat, lng in route_coords]
            avg_safety = np.mean(safety_scores)
            
            total_incidents = sum(
                self._count_nearby_incidents(lat, lng, radius_meters=100)
                for lat, lng in route_coords
            )
            
            return RoadRoute(
                route_points=route_coords,
                total_distance=total_distance,
                avg_safety_score=avg_safety,
                total_incidents=total_incidents,
                safety_grade=self.get_safety_grade(avg_safety),
                route_type='safest',
                waypoints=[(start_lat, start_lng), (end_lat, end_lng)],
                road_segments=self._get_road_segments(path)
            )
            
        except Exception as e:
            print(f"Error creating safety route: {e}")
            return None
    
    def _create_balanced_route(self, start_node: int, end_node: int,
                             start_lat: float, start_lng: float,
                             end_lat: float, end_lng: float,
                             max_distance: float) -> Optional[RoadRoute]:
        """Create balanced route between safety and distance"""
        try:
            # Use weighted cost function
            def balanced_cost(u, v, d):
                u_coords = (self.graph.nodes[u]['y'], self.graph.nodes[u]['x'])
                v_coords = (self.graph.nodes[v]['y'], self.graph.nodes[v]['x'])
                
                mid_lat = (u_coords[0] + v_coords[0]) / 2
                mid_lng = (u_coords[1] + v_coords[1]) / 2
                safety_score = self.get_safety_score(mid_lat, mid_lng)
                
                # Balanced weighting
                safety_factor = 1 + (100 - safety_score) / 200  # Less aggressive than safety route
                return d['length'] * safety_factor
            
            path = nx.astar_path(self.graph, start_node, end_node, weight=balanced_cost)
            
            # Calculate metrics
            route_coords = [(self.graph.nodes[node]['y'], self.graph.nodes[node]['x']) for node in path]
            
            total_distance = sum(
                self._calculate_distance(route_coords[i][0], route_coords[i][1],
                                       route_coords[i+1][0], route_coords[i+1][1])
                for i in range(len(route_coords) - 1)
            )
            
            safety_scores = [self.get_safety_score(lat, lng) for lat, lng in route_coords]
            avg_safety = np.mean(safety_scores)
            
            total_incidents = sum(
                self._count_nearby_incidents(lat, lng, radius_meters=100)
                for lat, lng in route_coords
            )
            
            return RoadRoute(
                route_points=route_coords,
                total_distance=total_distance,
                avg_safety_score=avg_safety,
                total_incidents=total_incidents,
                safety_grade=self.get_safety_grade(avg_safety),
                route_type='balanced',
                waypoints=[(start_lat, start_lng), (end_lat, end_lng)],
                road_segments=self._get_road_segments(path)
            )
            
        except Exception as e:
            print(f"Error creating balanced route: {e}")
            return None
    
    def _create_scenic_route(self, start_node: int, end_node: int,
                           start_lat: float, start_lng: float,
                           end_lat: float, end_lng: float,
                           max_distance: float) -> Optional[RoadRoute]:
        """Create scenic route that avoids major roads"""
        try:
            # Prefer smaller streets (residential areas)
            def scenic_cost(u, v, d):
                # Check if this is a major road
                highway_type = d.get('highway', 'residential')
                major_roads = ['motorway', 'trunk', 'primary', 'secondary']
                
                if highway_type in major_roads:
                    return d['length'] * 2  # Penalize major roads
                else:
                    return d['length'] * 0.8  # Prefer smaller roads
            
            path = nx.astar_path(self.graph, start_node, end_node, weight=scenic_cost)
            
            # Calculate metrics
            route_coords = [(self.graph.nodes[node]['y'], self.graph.nodes[node]['x']) for node in path]
            
            total_distance = sum(
                self._calculate_distance(route_coords[i][0], route_coords[i][1],
                                       route_coords[i+1][0], route_coords[i+1][1])
                for i in range(len(route_coords) - 1)
            )
            
            safety_scores = [self.get_safety_score(lat, lng) for lat, lng in route_coords]
            avg_safety = np.mean(safety_scores)
            
            total_incidents = sum(
                self._count_nearby_incidents(lat, lng, radius_meters=100)
                for lat, lng in route_coords
            )
            
            return RoadRoute(
                route_points=route_coords,
                total_distance=total_distance,
                avg_safety_score=avg_safety,
                total_incidents=total_incidents,
                safety_grade=self.get_safety_grade(avg_safety),
                route_type='scenic',
                waypoints=[(start_lat, start_lng), (end_lat, end_lng)],
                road_segments=self._get_road_segments(path)
            )
            
        except Exception as e:
            print(f"Error creating scenic route: {e}")
            return None
    
    def _select_best_road_route(self, route_options: List[RoadRoute], safety_weight: float) -> RoadRoute:
        """Select the best route based on safety weight preference"""
        if not route_options:
            raise Exception("No route options available")
        
        best_score = -1
        best_route = None
        
        for option in route_options:
            # Calculate combined score (0-1, higher is better)
            distance_score = 1 - (option.total_distance / max(opt.total_distance for opt in route_options))
            safety_score = option.avg_safety_score / 100
            
            # Combined score based on user preference
            combined_score = (1 - safety_weight) * distance_score + safety_weight * safety_score
            
            if combined_score > best_score:
                best_score = combined_score
                best_route = option
        
        return best_route
    
    def _get_road_segments(self, path: List[int]) -> List[Dict]:
        """Get road segment information for the path"""
        segments = []
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_data = self.graph.edges[u, v, 0]  # Get edge data
            
            segment = {
                'from_node': u,
                'to_node': v,
                'length': edge_data.get('length', 0),
                'highway': edge_data.get('highway', 'unknown'),
                'name': edge_data.get('name', 'Unnamed Street')
            }
            segments.append(segment)
        
        return segments
    
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
    
    def _count_nearby_incidents(self, lat: float, lng: float, radius_meters: float = 100) -> int:
        """Count incidents within radius of a point"""
        if self.incident_data.empty:
            return 0
        
        # Filter incidents within radius
        distances = []
        for _, incident in self.incident_data.iterrows():
            if pd.notna(incident['Latitude']) and pd.notna(incident['Longitude']):
                dist = self._calculate_distance(lat, lng, incident['Latitude'], incident['Longitude'])
                distances.append(dist)
            else:
                distances.append(float('inf'))
        
        # Count incidents within radius
        nearby_count = sum(1 for dist in distances if dist <= radius_meters)
        return nearby_count
    
    def _fallback_route(self, start_lat: float, start_lng: float,
                       end_lat: float, end_lng: float, safety_weight: float) -> Dict:
        """Fallback to simple straight-line routing when road network is unavailable"""
        print("Using fallback routing (straight line)")
        
        # Simple straight line route
        route_coords = [(start_lat, start_lng), (end_lat, end_lng)]
        total_distance = self._calculate_distance(start_lat, start_lng, end_lat, end_lng)
        
        # Calculate safety metrics
        safety_scores = [self.get_safety_score(lat, lng) for lat, lng in route_coords]
        avg_safety = np.mean(safety_scores)
        
        total_incidents = sum(
            self._count_nearby_incidents(lat, lng, radius_meters=100)
            for lat, lng in route_coords
        )
        
        fallback_route = RoadRoute(
            route_points=route_coords,
            total_distance=total_distance,
            avg_safety_score=avg_safety,
            total_incidents=total_incidents,
            safety_grade=self.get_safety_grade(avg_safety),
            route_type='fallback',
            waypoints=[(start_lat, start_lng), (end_lat, end_lng)],
            road_segments=[]
        )
        
        return {
            'success': True,
            'best_route': fallback_route,
            'all_options': [fallback_route],
            'routing_method': 'fallback'
        }
    
    def visualize_road_routes(self, route_options: List[RoadRoute], 
                            start_name: str = "Start", 
                            end_name: str = "End") -> folium.Map:
        """Create a map showing road-aware route options"""
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
                popup=f"{option.route_type.title()} Route<br>Safety: {option.avg_safety_score:.1f}<br>Distance: {option.total_distance:.0f}m"
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
        
        # Add incident heatmap
        incident_locations = self.incident_data[['Latitude', 'Longitude']].values.tolist()
        from folium.plugins import HeatMap
        HeatMap(
            incident_locations,
            radius=15,
            blur=10,
            max_zoom=13
        ).add_to(m)
        
        return m

# Example usage
def main():
    """Demonstrate the road-aware router"""
    
    # Initialize the road-aware router
    router = RoadAwareRouter('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')
    
    # Example coordinates in San Francisco
    start_lat, start_lng = 37.7694, -122.4862  # Golden Gate Park
    end_lat, end_lng = 37.8087, -122.4098      # Fisherman's Wharf
    
    print("=== Road-Aware Safe Route Finder Demo ===")
    print(f"Finding road-aware route from Golden Gate Park to Fisherman's Wharf...")
    
    # Find road-aware route
    result = router.find_road_route(
        start_lat, start_lng, end_lat, end_lng,
        safety_weight=0.7
    )
    
    if result['success']:
        best_route = result['best_route']
        print(f"✅ Route found using {result['routing_method']} routing!")
        print(f"Route Type: {best_route.route_type}")
        print(f"Total Distance: {best_route.total_distance:.0f} meters")
        print(f"Average Safety Score: {best_route.avg_safety_score:.1f}")
        print(f"Safety Grade: {best_route.safety_grade}")
        print(f"Total Incidents: {best_route.total_incidents}")
        
        # Show all options
        print(f"\nAll Route Options:")
        for option in result['all_options']:
            print(f"  {option.route_type}: {option.total_distance:.0f}m, "
                  f"Safety: {option.avg_safety_score:.1f}, Grade: {option.safety_grade}")
        
        # Create visualization
        print(f"\nCreating road-aware route map...")
        map_obj = router.visualize_road_routes(result['all_options'], "Golden Gate Park", "Fisherman's Wharf")
        map_obj.save('road_aware_routes.html')
        print("Map saved as 'road_aware_routes.html'")
        
    else:
        print("❌ Failed to find route")

if __name__ == "__main__":
    main() 