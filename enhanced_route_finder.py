import pandas as pd
import numpy as np
import folium
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
import heapq
from dataclasses import dataclass
import math
from scipy.spatial.distance import cdist
import warnings
from safe_route_finder import RoutePoint, SafeRouteFinder
warnings.filterwarnings('ignore')

@dataclass
class RouteOption:
    """Represents a route option with safety analysis"""
    route: List[RoutePoint]
    total_distance: float
    avg_safety_score: float
    total_incidents: int
    safety_grade: str
    route_type: str  # 'direct', 'safer', 'safest', 'balanced'
    waypoints: List[Tuple[float, float]]

class EnhancedRouteFinder(SafeRouteFinder):
    def __init__(self, incident_data_path: str):
        """Initialize the enhanced route finder"""
        super().__init__(incident_data_path)
        self.route_options = []
        
    def find_optimal_safe_route(self, 
                               start_lat: float, 
                               start_lng: float, 
                               end_lat: float, 
                               end_lng: float,
                               safety_weight: float = 0.7,
                               max_distance_factor: float = 2.0) -> Dict:
        """
        Find the optimal safe route by generating multiple options and selecting the best one
        
        Args:
            start_lat, start_lng: Starting coordinates
            end_lat, end_lng: Ending coordinates
            safety_weight: Weight given to safety vs distance (0-1)
            max_distance_factor: Maximum route length as factor of direct distance
        
        Returns:
            Dictionary with the best route and all options
        """
        print(f"Finding optimal safe route from ({start_lat:.4f}, {start_lng:.4f}) to ({end_lat:.4f}, {end_lng:.4f})")
        
        # Generate multiple route options
        self.route_options = self._generate_route_options(
            start_lat, start_lng, end_lat, end_lng, max_distance_factor
        )
        
        if not self.route_options:
            raise Exception("No valid routes found")
        
        # Select the best route based on safety weight
        best_route = self._select_best_route(safety_weight)
        
        # Get detailed analysis
        summary = self.get_route_summary(best_route.route)
        recommendations = self.get_safety_recommendations(best_route.route)
        
        return {
            'best_route': best_route,
            'all_options': self.route_options,
            'summary': summary,
            'recommendations': recommendations,
            'route_comparison': self._compare_routes()
        }
    
    def _generate_route_options(self, 
                               start_lat: float, 
                               start_lng: float, 
                               end_lat: float, 
                               end_lng: float,
                               max_distance_factor: float) -> List[RouteOption]:
        """Generate multiple route options with different safety strategies"""
        options = []
        
        # Calculate direct distance
        direct_distance = self.calculate_distance(start_lat, start_lng, end_lat, end_lng)
        max_distance = direct_distance * max_distance_factor
        
        # Create safety grid if not already created
        if self.safety_grid is None:
            bounds = (
                min(start_lat, end_lat) - 0.02,
                min(start_lng, end_lng) - 0.02,
                max(start_lat, end_lat) + 0.02,
                max(start_lng, end_lng) + 0.02
            )
            self.create_safety_grid(bounds)
        
        # Option 1: Direct route (fastest)
        direct_route = self._create_direct_route(start_lat, start_lng, end_lat, end_lng)
        if direct_route:
            options.append(direct_route)
        
        # Option 2: Safety-optimized route
        safe_route = self._create_safety_optimized_route(start_lat, start_lng, end_lat, end_lng, max_distance)
        if safe_route:
            options.append(safe_route)
        
        # Option 3: Balanced route
        balanced_route = self._create_balanced_route(start_lat, start_lng, end_lat, end_lng, max_distance)
        if balanced_route:
            options.append(balanced_route)
        
        # Option 4: Perimeter route (avoids center areas)
        perimeter_route = self._create_perimeter_route(start_lat, start_lng, end_lat, end_lng, max_distance)
        if perimeter_route:
            options.append(perimeter_route)
        
        # Option 5: Multi-path route (combines multiple safe paths)
        multipath_route = self._create_multipath_route(start_lat, start_lng, end_lat, end_lng, max_distance)
        if multipath_route:
            options.append(multipath_route)
        
        return options
    
    def _create_direct_route(self, start_lat: float, start_lng: float, 
                           end_lat: float, end_lng: float) -> Optional[RouteOption]:
        """Create a direct route (fastest path)"""
        try:
            # Simple direct route with minimal waypoints
            waypoints = [(start_lat, start_lng), (end_lat, end_lng)]
            route = self._find_optimal_path(waypoints, 0.1)  # Low safety weight for speed
            
            if route:
                summary = self.get_route_summary(route)
                return RouteOption(
                    route=route,
                    total_distance=summary['total_distance_meters'],
                    avg_safety_score=summary['avg_safety_score'],
                    total_incidents=summary['total_incidents_along_route'],
                    safety_grade=summary['safety_grade'],
                    route_type='direct',
                    waypoints=waypoints
                )
        except Exception as e:
            print(f"Error creating direct route: {e}")
        return None
    
    def _create_safety_optimized_route(self, start_lat: float, start_lng: float,
                                     end_lat: float, end_lng: float, max_distance: float) -> Optional[RouteOption]:
        """Create a route optimized for maximum safety"""
        try:
            # Generate waypoints that avoid high-incident areas
            waypoints = self._generate_safety_waypoints(start_lat, start_lng, end_lat, end_lng, max_distance, safety_focus=True)
            route = self._find_optimal_path(waypoints, 0.9)  # High safety weight
            
            if route:
                summary = self.get_route_summary(route)
                return RouteOption(
                    route=route,
                    total_distance=summary['total_distance_meters'],
                    avg_safety_score=summary['avg_safety_score'],
                    total_incidents=summary['total_incidents_along_route'],
                    safety_grade=summary['safety_grade'],
                    route_type='safest',
                    waypoints=waypoints
                )
        except Exception as e:
            print(f"Error creating safety route: {e}")
        return None
    
    def _create_balanced_route(self, start_lat: float, start_lng: float,
                             end_lat: float, end_lng: float, max_distance: float) -> Optional[RouteOption]:
        """Create a balanced route between safety and distance"""
        try:
            waypoints = self._generate_safety_waypoints(start_lat, start_lng, end_lat, end_lng, max_distance, safety_focus=False)
            route = self._find_optimal_path(waypoints, 0.5)  # Balanced weight
            
            if route:
                summary = self.get_route_summary(route)
                return RouteOption(
                    route=route,
                    total_distance=summary['total_distance_meters'],
                    avg_safety_score=summary['avg_safety_score'],
                    total_incidents=summary['total_incidents_along_route'],
                    safety_grade=summary['safety_grade'],
                    route_type='balanced',
                    waypoints=waypoints
                )
        except Exception as e:
            print(f"Error creating balanced route: {e}")
        return None
    
    def _create_perimeter_route(self, start_lat: float, start_lng: float,
                              end_lat: float, end_lng: float, max_distance: float) -> Optional[RouteOption]:
        """Create a route that follows the perimeter to avoid center areas"""
        try:
            waypoints = self._generate_perimeter_waypoints(start_lat, start_lng, end_lat, end_lng, max_distance)
            route = self._find_optimal_path(waypoints, 0.7)  # Medium-high safety weight
            
            if route:
                summary = self.get_route_summary(route)
                return RouteOption(
                    route=route,
                    total_distance=summary['total_distance_meters'],
                    avg_safety_score=summary['avg_safety_score'],
                    total_incidents=summary['total_incidents_along_route'],
                    safety_grade=summary['safety_grade'],
                    route_type='perimeter',
                    waypoints=waypoints
                )
        except Exception as e:
            print(f"Error creating perimeter route: {e}")
        return None
    
    def _create_multipath_route(self, start_lat: float, start_lng: float,
                              end_lat: float, end_lng: float, max_distance: float) -> Optional[RouteOption]:
        """Create a route that combines multiple safe paths"""
        try:
            waypoints = self._generate_multipath_waypoints(start_lat, start_lng, end_lat, end_lng, max_distance)
            route = self._find_optimal_path(waypoints, 0.6)  # Medium safety weight
            
            if route:
                summary = self.get_route_summary(route)
                return RouteOption(
                    route=route,
                    total_distance=summary['total_distance_meters'],
                    avg_safety_score=summary['avg_safety_score'],
                    total_incidents=summary['total_incidents_along_route'],
                    safety_grade=summary['safety_grade'],
                    route_type='multipath',
                    waypoints=waypoints
                )
        except Exception as e:
            print(f"Error creating multipath route: {e}")
        return None
    
    def _generate_safety_waypoints(self, start_lat: float, start_lng: float,
                                 end_lat: float, end_lng: float, max_distance: float,
                                 safety_focus: bool = True) -> List[Tuple[float, float]]:
        """Generate waypoints optimized for safety"""
        waypoints = [(start_lat, start_lng)]
        
        # Calculate bearing and distance
        bearing = self._calculate_bearing(start_lat, start_lng, end_lat, end_lng)
        direct_distance = self.calculate_distance(start_lat, start_lng, end_lat, end_lng)
        
        # Number of waypoints based on distance and safety focus
        if safety_focus:
            num_waypoints = max(5, int(direct_distance / 200))  # More waypoints for safety
        else:
            num_waypoints = max(3, int(direct_distance / 300))
        
        for i in range(1, num_waypoints):
            progress = i / num_waypoints
            
            # Base position along direct route
            base_lat = start_lat + (end_lat - start_lat) * progress
            base_lng = start_lng + (end_lng - start_lng) * progress
            
            # Find safer nearby location
            best_lat, best_lng = self._find_safest_nearby_location(base_lat, base_lng, safety_focus)
            
            waypoints.append((best_lat, best_lng))
        
        waypoints.append((end_lat, end_lng))
        return waypoints
    
    def _generate_perimeter_waypoints(self, start_lat: float, start_lng: float,
                                    end_lat: float, end_lng: float, max_distance: float) -> List[Tuple[float, float]]:
        """Generate waypoints that follow the perimeter"""
        waypoints = [(start_lat, start_lng)]
        
        # Calculate center point
        center_lat = (start_lat + end_lat) / 2
        center_lng = (start_lng + end_lng) / 2
        
        # Calculate radius for perimeter
        radius = 0.005  # ~500 meters
        
        # Generate perimeter waypoints
        num_perimeter_points = 4
        for i in range(1, num_perimeter_points + 1):
            angle = (i / (num_perimeter_points + 1)) * 2 * math.pi
            
            # Calculate perimeter point
            perim_lat = center_lat + radius * math.cos(angle)
            perim_lng = center_lng + radius * math.sin(angle)
            
            # Find safe location near perimeter
            safe_lat, safe_lng = self._find_safest_nearby_location(perim_lat, perim_lng, True)
            waypoints.append((safe_lat, safe_lng))
        
        waypoints.append((end_lat, end_lng))
        return waypoints
    
    def _generate_multipath_waypoints(self, start_lat: float, start_lng: float,
                                    end_lat: float, end_lng: float, max_distance: float) -> List[Tuple[float, float]]:
        """Generate waypoints using multiple path strategies"""
        waypoints = [(start_lat, start_lng)]
        
        # Create multiple path options and combine the best segments
        paths = []
        
        # Path 1: Direct with safety detours
        path1 = self._generate_safety_waypoints(start_lat, start_lng, end_lat, end_lng, max_distance, True)
        paths.append(path1)
        
        # Path 2: Perimeter approach
        path2 = self._generate_perimeter_waypoints(start_lat, start_lng, end_lat, end_lng, max_distance)
        paths.append(path2)
        
        # Combine best segments from each path
        combined_waypoints = self._combine_best_path_segments(paths, start_lat, start_lng, end_lat, end_lng)
        
        return combined_waypoints
    
    def _find_safest_nearby_location(self, lat: float, lng: float, safety_focus: bool = True) -> Tuple[float, float]:
        """Find the safest location within a radius of the given point"""
        best_lat, best_lng = lat, lng
        best_safety = self.get_safety_score(lat, lng)
        
        # Search radius based on safety focus
        if safety_focus:
            search_radius = 0.002  # ~200 meters
            num_attempts = 12
        else:
            search_radius = 0.001  # ~100 meters
            num_attempts = 8
        
        for attempt in range(num_attempts):
            angle = (attempt / num_attempts) * 2 * math.pi
            test_lat = lat + search_radius * math.cos(angle)
            test_lng = lng + search_radius * math.sin(angle)
            
            test_safety = self.get_safety_score(test_lat, test_lng)
            
            if test_safety > best_safety:
                best_lat, best_lng = test_lat, test_lng
                best_safety = test_safety
        
        return best_lat, best_lng
    
    def _combine_best_path_segments(self, paths: List[List[Tuple[float, float]]], 
                                  start_lat: float, start_lng: float,
                                  end_lat: float, end_lng: float) -> List[Tuple[float, float]]:
        """Combine the best segments from multiple paths"""
        combined = [(start_lat, start_lng)]
        
        # For simplicity, alternate between paths
        max_points = max(len(path) for path in paths)
        
        for i in range(1, max_points - 1):
            path_idx = i % len(paths)
            if i < len(paths[path_idx]):
                combined.append(paths[path_idx][i])
        
        combined.append((end_lat, end_lng))
        return combined
    
    def _select_best_route(self, safety_weight: float) -> RouteOption:
        """Select the best route based on safety weight preference"""
        if not self.route_options:
            raise Exception("No route options available")
        
        best_score = -1
        best_route = None
        
        for option in self.route_options:
            # Calculate combined score (0-1, higher is better)
            distance_score = 1 - (option.total_distance / max(opt.total_distance for opt in self.route_options))
            safety_score = option.avg_safety_score / 100
            
            # Combined score based on user preference
            combined_score = (1 - safety_weight) * distance_score + safety_weight * safety_score
            
            if combined_score > best_score:
                best_score = combined_score
                best_route = option
        
        return best_route
    
    def _compare_routes(self) -> List[Dict]:
        """Compare all route options"""
        comparison = []
        
        for option in self.route_options:
            comparison.append({
                'route_type': option.route_type,
                'total_distance': float(option.total_distance),
                'avg_safety_score': float(option.avg_safety_score),
                'total_incidents': int(option.total_incidents),
                'safety_grade': str(option.safety_grade),
                'waypoint_count': int(len(option.waypoints))
            })
        
        return comparison
    
    def visualize_all_routes(self, route_options: List[RouteOption], 
                           start_name: str = "Start", 
                           end_name: str = "End") -> folium.Map:
        """Create a map showing all route options"""
        if not route_options:
            return None
        
        # Calculate center
        all_lats = []
        all_lngs = []
        for option in route_options:
            for point in option.route:
                all_lats.append(point.lat)
                all_lngs.append(point.lng)
        
        center_lat = sum(all_lats) / len(all_lats)
        center_lng = sum(all_lngs) / len(all_lngs)
        
        # Create map
        m = folium.Map(location=[center_lat, center_lng], zoom_start=13)
        
        # Color scheme for different routes
        colors = ['blue', 'green', 'red', 'orange', 'purple', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
        
        # Add each route option
        for i, option in enumerate(route_options):
            color = colors[i % len(colors)]
            
            # Add route line
            route_coords = [(point.lat, point.lng) for point in option.route]
            
            folium.PolyLine(
                locations=route_coords,
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
                else:  # Intermediate waypoints
                    folium.CircleMarker(
                        waypoint,
                        radius=6,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.6,
                        popup=f"Waypoint {j} - {option.route_type.title()} Route"
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
    """Demonstrate the enhanced route finder"""
    
    # Initialize the enhanced route finder
    finder = EnhancedRouteFinder('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')
    
    # Example coordinates in San Francisco
    start_lat, start_lng = 37.7694, -122.4862  # Golden Gate Park
    end_lat, end_lng = 37.8087, -122.4098      # Fisherman's Wharf
    
    print("=== Enhanced Safe Route Finder Demo ===")
    print(f"Finding optimal route from Golden Gate Park to Fisherman's Wharf...")
    
    # Find optimal route with different safety preferences
    for safety_weight in [0.3, 0.7, 0.9]:
        print(f"\n--- Safety Weight: {safety_weight} ---")
        
        result = finder.find_optimal_safe_route(
            start_lat, start_lng, end_lat, end_lng,
            safety_weight=safety_weight
        )
        
        best_route = result['best_route']
        print(f"Selected Route Type: {best_route.route_type}")
        print(f"Total Distance: {best_route.total_distance:.0f} meters")
        print(f"Average Safety Score: {best_route.avg_safety_score:.1f}")
        print(f"Safety Grade: {best_route.safety_grade}")
        print(f"Total Incidents: {best_route.total_incidents}")
    
    # Show route comparison
    print(f"\n=== Route Comparison ===")
    for route_info in result['route_comparison']:
        print(f"{route_info['route_type'].title()}: "
              f"Distance={route_info['total_distance']:.0f}m, "
              f"Safety={route_info['avg_safety_score']:.1f}, "
              f"Grade={route_info['safety_grade']}")
    
    # Create visualization
    print(f"\nCreating route comparison map...")
    map_obj = finder.visualize_all_routes(result['all_options'], "Golden Gate Park", "Fisherman's Wharf")
    map_obj.save('enhanced_route_comparison.html')
    print("Map saved as 'enhanced_route_comparison.html'")

if __name__ == "__main__":
    main() 