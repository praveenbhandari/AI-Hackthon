#!/usr/bin/env python
"""
Debug script for safety crew execution
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bc.crew import Bc
import json

def test_safety_crew():
    """Test safety crew execution with simple inputs"""
    print("🔧 Testing Safety Crew Execution...")
    
    try:
        # Create crew instance
        crew_instance = Bc()
        print("✅ Crew instance created")
        
        # Prepare simple inputs
        inputs = {
            'topic': 'Safety Route Planning',
            'current_year': '2025',
            'start_lat': 37.7694,
            'start_lng': -122.4862,
            'end_lat': 37.8087,
            'end_lng': -122.4098,
            'safety_weight': 0.7,
            'safety_analysis_request': 'Analyze safety patterns in San Francisco',
            'route_planning_request': 'Find safe route from Golden Gate Park to Fisherman\'s Wharf',
            'user_preferences': 'Safety-focused, walking preferred',
            'safety_requirements': 'Avoid high-crime areas, well-lit routes'
        }
        
        print("✅ Inputs prepared")
        print(f"Inputs: {json.dumps(inputs, indent=2)}")
        
        # Execute safety crew
        print("🚀 Executing safety crew...")
        result = crew_instance.safety_crew().kickoff(inputs=inputs)
        
        print("✅ Safety crew executed successfully")
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error executing safety crew: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_safety_crew() 