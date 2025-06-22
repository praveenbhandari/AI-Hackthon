import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from food_agent_client import FoodAgent
import asyncio

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the food agent
food_agent = FoodAgent(use_typescript=True)

# Configuration
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
PORT = 5001  # Explicitly set port to 5001
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

@app.route('/')
def index():
    """Render the main page with the food recommendation interface."""
    return render_template('index.html', google_api_key=GOOGLE_PLACES_API_KEY)

@app.route('/api/search', methods=['POST'])
def search():
    """Process a food query and return restaurant recommendations."""
    data = request.json
    query = data.get('query', '')
    location = data.get('location', 'San Francisco')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Process the query using our FoodAgent asynchronously
        result = asyncio.run(food_agent.process_query(query, location))
        
        # Log the original and processed queries
        app.logger.info(f"Original query: '{query}' → Processed: '{result['processed_query']}'")
        
        # Include any sorting preferences in the log
        query_analysis = result.get('query_analysis', {})
        if query_analysis and query_analysis.get('sortBy'):
            app.logger.info(f"Sort preference detected: {query_analysis.get('sortBy')}")
        
        # Return the results
        return jsonify({
            'success': result['success'],
            'results': result.get('restaurants', []),  # Ensure results is always an array
            'count': len(result.get('restaurants', [])),
            'processed_query': result.get('processed_query', query),
            'original_query': result.get('original_query', query),
            'query_analysis': result.get('query_analysis', {}),  # Include the query analysis
            'message': result.get('message', '')
        })
    except Exception as e:
        app.logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500

# We're now using the new food_agent_client module with Letta SDK for all search functionality

if __name__ == '__main__':
    print(f"Starting Flask app on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
