#!/usr/bin/env python
import sys
import warnings
import os

from datetime import datetime

from bc.crew import Bc

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# Default SFO BART schedule file path
DEFAULT_SCHEDULE_FILE = "./src/sfo_bart_schedule.csv"

def run():
    """
    Run the research crew (default).
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }
    
    try:
        # Use research-only crew to avoid transit task variable conflicts
        Bc().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the research crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Bc().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Bc().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the research crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Bc().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_transit_crew():
    """
    Run the transit crew with proper inputs.
    """
    inputs = {
        'topic': 'Bay Area Transit Planning',
        'current_year': str(datetime.now().year),
        'user_request': 'I want to go from Salesforce Transit Center to Richmond BART at 08:00 AM',
        'schedule_file': DEFAULT_SCHEDULE_FILE if os.path.exists(DEFAULT_SCHEDULE_FILE) else '',
        'origin': 'Salesforce Transit Center',
        'destination': 'Richmond BART',
        'time': '08:00'
    }
    
    try:
        Bc().transit_crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the transit crew: {e}")

def run_safety_crew():
    """
    Run the safety crew with proper inputs.
    """
    inputs = {
        'topic': 'Safety Route Planning',
        'current_year': str(datetime.now().year),
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
    
    try:
        Bc().safety_crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the safety crew: {e}")

def run_full_crew():
    """
    Run the full crew with all tasks (requires all variables).
    """
    inputs = {
        'topic': 'AI LLMs and Transit Planning',
        'current_year': str(datetime.now().year),
        'user_request': 'Analyze AI LLMs and provide insights about the current state of the technology',
        'schedule_file': DEFAULT_SCHEDULE_FILE if os.path.exists(DEFAULT_SCHEDULE_FILE) else '',
        'origin': 'AI Research',
        'destination': 'Machine Learning',
        'time': '09:00'
    }
    
    try:
        Bc().full_crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the full crew: {e}")
