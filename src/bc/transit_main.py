#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from bc.crew import Bc
from bc.tools import schedule_processor
import os

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Default SFO BART schedule file path
DEFAULT_SCHEDULE_FILE = "/Users/praveenbhandari/Desktop/BC/bc/src/sfo_bart_schedule.csv"

def check_schedule_file(file_path: str) -> bool:
    """
    Check if the schedule file exists and is accessible.
    """
    if not os.path.exists(file_path):
        print(f"❌ Schedule file not found: {file_path}")
        return False
    
    if not os.path.isfile(file_path):
        print(f"❌ Path is not a file: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            if not first_line or ',' not in first_line:
                print(f"❌ File does not appear to be a valid CSV: {file_path}")
                return False
        return True
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def run_transit_planning():
    """
    Run the transit planning crew for route optimization.
    """
    print("🚌 Bay Area Transit Route Planner")
    print("=" * 50)
    
    # Check default file first
    if check_schedule_file(DEFAULT_SCHEDULE_FILE):
        print(f"✅ Found SFO BART schedule: {DEFAULT_SCHEDULE_FILE}")
        schedule_file = DEFAULT_SCHEDULE_FILE
    else:
        # Get user input for alternative file
        schedule_file = input("Enter the path to your transit schedule CSV file: ").strip()
        if not check_schedule_file(schedule_file):
            print("❌ Invalid file path. Exiting.")
            return None
    
    # Get user input
    user_request = input("Enter your transit query (e.g., 'I want to go from CSU East Bay to Hayward BART at 11:00 AM'): ")
    
    inputs = {
        'topic': 'Bay Area Transit Planning',
        'current_year': str(datetime.now().year),
        'user_request': user_request,
        'schedule_file': schedule_file
    }
    
    try:
        print(f"\n🔄 Loading transit data from: {schedule_file}")
        print("This may take a moment for large files...")
        
        # Create crew instance
        crew_instance = Bc()
        
        # Run transit planning task
        result = crew_instance.transit_planning_task().execute(inputs=inputs)
        print("\n🧾 Transit Plan Generated:")
        print(result)
        
        return result
    except Exception as e:
        print(f"❌ Error during transit planning: {e}")
        raise Exception(f"An error occurred while running the transit planning: {e}")

def run_transit_analysis():
    """
    Run the transit analysis crew for system insights.
    """
    print("📊 Bay Area Transit System Analysis")
    print("=" * 50)
    
    # Check default file first
    if check_schedule_file(DEFAULT_SCHEDULE_FILE):
        print(f"✅ Found SFO BART schedule: {DEFAULT_SCHEDULE_FILE}")
        schedule_file = DEFAULT_SCHEDULE_FILE
    else:
        # Get user input for alternative file
        schedule_file = input("Enter the path to your transit schedule CSV file: ").strip()
        if not check_schedule_file(schedule_file):
            print("❌ Invalid file path. Exiting.")
            return None
    
    inputs = {
        'topic': 'Bay Area Transit System Analysis',
        'current_year': str(datetime.now().year),
        'schedule_file': schedule_file
    }
    
    try:
        print(f"\n🔄 Loading transit data from: {schedule_file}")
        print("This may take a moment for large files...")
        
        # Create crew instance
        crew_instance = Bc()
        
        # Run transit analysis task
        result = crew_instance.transit_analysis_task().execute(inputs=inputs)
        print("\n📈 Transit Analysis Generated:")
        print(result)
        
        return result
    except Exception as e:
        print(f"❌ Error during transit analysis: {e}")
        raise Exception(f"An error occurred while running the transit analysis: {e}")

def run_route_optimization():
    """
    Run the route optimization crew for finding the best routes.
    """
    print("🎯 Route Optimization Specialist")
    print("=" * 50)
    
    # Check default file first
    if check_schedule_file(DEFAULT_SCHEDULE_FILE):
        print(f"✅ Found SFO BART schedule: {DEFAULT_SCHEDULE_FILE}")
        schedule_file = DEFAULT_SCHEDULE_FILE
    else:
        # Get user input for alternative file
        schedule_file = input("Enter the path to your transit schedule CSV file: ").strip()
        if not check_schedule_file(schedule_file):
            print("❌ Invalid file path. Exiting.")
            return None
    
    origin = input("Enter origin location: ")
    destination = input("Enter destination location: ")
    time = input("Enter departure time (HH:MM format): ")
    
    inputs = {
        'topic': 'Route Optimization',
        'current_year': str(datetime.now().year),
        'origin': origin,
        'destination': destination,
        'time': time,
        'schedule_file': schedule_file
    }
    
    try:
        print(f"\n🔄 Loading transit data from: {schedule_file}")
        print("This may take a moment for large files...")
        
        # Create crew instance
        crew_instance = Bc()
        
        # Run route optimization task
        result = crew_instance.route_optimization_task().execute(inputs=inputs)
        print("\n🎯 Optimized Routes Generated:")
        print(result)
        
        return result
    except Exception as e:
        print(f"❌ Error during route optimization: {e}")
        raise Exception(f"An error occurred while running the route optimization: {e}")

def run_full_transit_crew():
    """
    Run the full transit crew with all agents working together.
    """
    print("🚌 Full Bay Area Transit Crew")
    print("=" * 50)
    
    # Check default file first
    if check_schedule_file(DEFAULT_SCHEDULE_FILE):
        print(f"✅ Found SFO BART schedule: {DEFAULT_SCHEDULE_FILE}")
        schedule_file = DEFAULT_SCHEDULE_FILE
    else:
        # Get user input for alternative file
        schedule_file = input("Enter the path to your transit schedule CSV file: ").strip()
        if not check_schedule_file(schedule_file):
            print("❌ Invalid file path. Exiting.")
            return None
    
    user_request = input("Enter your transit query: ")
    
    inputs = {
        'topic': 'Bay Area Transit Planning and Analysis',
        'current_year': str(datetime.now().year),
        'user_request': user_request,
        'schedule_file': schedule_file
    }
    
    try:
        print(f"\n🔄 Loading transit data from: {schedule_file}")
        print("This may take a moment for large files...")
        
        # Create and run the full crew
        result = Bc().crew().kickoff(inputs=inputs)
        print("\n🚌 Full Transit Analysis Complete:")
        print(result)
        
        return result
    except Exception as e:
        print(f"❌ Error during full transit crew execution: {e}")
        raise Exception(f"An error occurred while running the full transit crew: {e}")

def show_file_info():
    """
    Show information about the SFO BART schedule file.
    """
    print("📁 SFO BART Schedule File Information")
    print("=" * 50)
    
    if check_schedule_file(DEFAULT_SCHEDULE_FILE):
        try:
            import pandas as pd
            df = pd.read_csv(DEFAULT_SCHEDULE_FILE, nrows=5)
            print(f"✅ File: {DEFAULT_SCHEDULE_FILE}")
            print(f"📊 Columns: {list(df.columns)}")
            print(f"📈 Sample data preview:")
            print(df.head())
            
            # Get file size
            file_size = os.path.getsize(DEFAULT_SCHEDULE_FILE)
            file_size_mb = file_size / (1024 * 1024)
            print(f"📏 File size: {file_size_mb:.2f} MB")
            
            # Count lines
            with open(DEFAULT_SCHEDULE_FILE, 'r') as f:
                line_count = sum(1 for _ in f)
            print(f"📝 Total lines: {line_count:,}")
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    else:
        print(f"❌ File not found: {DEFAULT_SCHEDULE_FILE}")

def main():
    """
    Main function to run different transit operations.
    """
    print("🚌 Bay Area Transit CrewAI System")
    print("=" * 50)
    print("Choose an operation:")
    print("1. Transit Planning (Route Planning)")
    print("2. Transit Analysis (System Insights)")
    print("3. Route Optimization (Best Routes)")
    print("4. Full Transit Crew (All Operations)")
    print("5. Show File Information")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        run_transit_planning()
    elif choice == "2":
        run_transit_analysis()
    elif choice == "3":
        run_route_optimization()
    elif choice == "4":
        run_full_transit_crew()
    elif choice == "5":
        show_file_info()
    elif choice == "6":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    main() 