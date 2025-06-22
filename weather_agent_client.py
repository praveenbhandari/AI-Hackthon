"""
Weather Agent client that processes weather data and provides clothing recommendations.
"""

import os
import json
import subprocess
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WeatherAgent:
    """
    Weather Agent client that processes weather data and provides clothing recommendations.
    This implementation uses the TypeScript agent via Node.js subprocess.
    """
    
    def __init__(self):
        """
        Initialize the Weather Agent client
        """
        logger.info("Initializing Weather Agent client")
    
    async def get_recommendation(self, location: str = "San Francisco"):
        """
        Get weather data and clothing recommendations for a location
        
        Args:
            location: The location to get weather for (default: "San Francisco")
            
        Returns:
            Dictionary with weather data, clothing recommendations, and reasoning
        """
        logger.info(f"Getting weather recommendation for: '{location}'")
        
        try:
            # Call the TypeScript implementation via Node.js subprocess
            return self._process_typescript(location)
        except Exception as e:
            logger.error(f"Error getting weather recommendation: {str(e)}")
            return {
                "success": False,
                "message": f"Error getting weather recommendation: {str(e)}"
            }
    
    def _process_typescript(self, location: str):
        """
        Process a location using the JavaScript implementation
        
        Args:
            location: The location to get weather for
            
        Returns:
            Dictionary with weather data, clothing recommendations, and reasoning
        """
        try:
            # Run the JavaScript script with Node.js
            cmd = ["node", "agentic-weather.js", location]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the output to extract the JSON result
            output = result.stdout
            logger.debug(f"JavaScript output: {output}")
            
            # Find the JSON part in the output (after "Results:")
            results_marker = "Results:\n"
            results_pos = output.find(results_marker)
            
            if results_pos == -1:
                logger.error(f"Could not find 'Results:' marker in output: {output}")
                raise ValueError("Could not find 'Results:' marker in output")
                
            json_str = output[results_pos + len(results_marker):].strip()
            logger.debug(f"JSON string to parse: {json_str}")
            data = json.loads(json_str)
            
            return data
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running JavaScript: {e.stderr}")
            return {
                "success": False,
                "message": f"Error running JavaScript: {e.stderr}"
            }
        except Exception as e:
            logger.error(f"Error processing JavaScript result: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing JavaScript result: {str(e)}"
            }

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = WeatherAgent()
        result = await agent.get_recommendation("London")
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())
