#!/usr/bin/env python3
"""
Enhanced Safe Route Finder Demo
Demonstrates the system that generates multiple route options and automatically selects the safest one.
"""

from enhanced_route_finder import EnhancedRouteFinder
import time

def main():
    print("=" * 60)
    print("🚶 Enhanced Safe Route Finder Demo")
    print("=" * 60)
    print()
    
    # Initialize the enhanced route finder
    print("📊 Loading San Francisco police incident data...")
    finder = EnhancedRouteFinder('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')
    print("✅ Data loaded successfully!")
    print()
    
    # Example coordinates in San Francisco
    start_lat, start_lng = 37.7694, -122.4862  # Golden Gate Park
    end_lat, end_lng = 37.8087, -122.4098      # Fisherman's Wharf
    
    print(f"📍 Route: Golden Gate Park → Fisherman's Wharf")
    print(f"   Start: ({start_lat:.4f}, {start_lng:.4f})")
    print(f"   End:   ({end_lat:.4f}, {end_lng:.4f})")
    print()
    
    # Test different safety preferences
    safety_preferences = [
        (0.3, "Speed Priority"),
        (0.5, "Balanced"),
        (0.7, "Safety Priority"),
        (0.9, "Maximum Safety")
    ]
    
    for safety_weight, description in safety_preferences:
        print(f"🔍 Testing {description} (Safety Weight: {safety_weight*100:.0f}%)")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Find optimal route
            result = finder.find_optimal_safe_route(
                start_lat, start_lng, end_lat, end_lng,
                safety_weight=safety_weight
            )
            
            elapsed_time = time.time() - start_time
            
            # Display results
            best_route = result['best_route']
            print(f"⏱️  Processing time: {elapsed_time:.2f} seconds")
            print(f"⭐ Selected Route: {best_route.route_type.upper()}")
            print(f"📏 Distance: {best_route.total_distance:.0f} meters")
            print(f"🛡️  Safety Score: {best_route.avg_safety_score:.1f}/100")
            print(f"🚨 Incidents: {best_route.total_incidents}")
            print(f"📊 Grade: {best_route.safety_grade}")
            print()
            
            # Show route comparison
            print("📋 All Route Options:")
            print(f"{'Type':<12} {'Distance':<10} {'Safety':<8} {'Incidents':<10} {'Grade':<6}")
            print("-" * 50)
            
            for route_info in result['route_comparison']:
                marker = "⭐" if route_info['route_type'] == best_route.route_type else "  "
                print(f"{marker} {route_info['route_type']:<10} "
                      f"{route_info['total_distance']:<9.0f}m "
                      f"{route_info['avg_safety_score']:<7.1f} "
                      f"{route_info['total_incidents']:<9} "
                      f"{route_info['safety_grade']:<6}")
            
            print()
            
            # Show recommendations
            if result['recommendations']:
                print("💡 Safety Recommendations:")
                for i, rec in enumerate(result['recommendations'][:3], 1):  # Show first 3
                    print(f"   {i}. {rec}")
                print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
        
        print("=" * 60)
        print()
    
    # Create visualization
    print("🗺️  Creating route comparison map...")
    try:
        result = finder.find_optimal_safe_route(start_lat, start_lng, end_lat, end_lng, safety_weight=0.7)
        map_obj = finder.visualize_all_routes(
            result['all_options'],
            "Golden Gate Park",
            "Fisherman's Wharf"
        )
        map_obj.save('enhanced_route_demo.html')
        print("✅ Map saved as 'enhanced_route_demo.html'")
    except Exception as e:
        print(f"❌ Error creating map: {e}")
    
    print()
    print("🎉 Demo completed!")
    print()
    print("Key Features Demonstrated:")
    print("• Multiple route generation strategies")
    print("• Automatic selection based on safety preferences")
    print("• Comprehensive route comparison")
    print("• Safety analysis and recommendations")
    print("• Interactive map visualization")
    print()
    print("To run the web interface:")
    print("  python web_interface.py")
    print()
    print("To view the demo map:")
    print("  open enhanced_route_demo.html")

if __name__ == "__main__":
    main() 