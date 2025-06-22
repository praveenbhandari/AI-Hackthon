from letta_client import Letta
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

class FoodAgent:
    """
    Food Agent client that processes natural language food queries and returns restaurant recommendations.
    This implementation uses the new Letta client and can either:
    1. Call the TypeScript implementation via Node.js subprocess
    2. Use the Python Letta client directly
    """
    
    def __init__(self, use_typescript=True):
        """
        Initialize the Food Agent client
        
        Args:
            use_typescript: Whether to use the TypeScript implementation (True) or Python (False)
        """
        self.use_typescript = use_typescript
        
        if not use_typescript:
            # Initialize Python Letta client
            self.client = Letta(base_url="http://localhost:8283")
            # If you have a Letta API key, you can use it like this:
            # self.client = Letta(token=os.getenv("LETTA_API_KEY"))
    
    async def process_query(self, query_text: str, location: str = "San Francisco"):
        """
        Process a natural language food query and return restaurant recommendations
        
        Args:
            query_text: The user's food query (e.g., "I want spicy Indian food")
            location: The location to search in (default: "San Francisco")
            
        Returns:
            Dictionary with restaurant recommendations or error message
        """
        logger.info(f"Processing query: '{query_text}' in {location}")
        
        try:
            if self.use_typescript:
                # Call the TypeScript implementation via Node.js subprocess
                return self._process_query_typescript(query_text, location)
            else:
                # Use the Python Letta client directly
                # This is a placeholder for the Python implementation
                # You would need to implement this based on your specific needs
                return {"success": False, "message": "Python Letta client implementation not yet available"}
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "restaurants": [],
                "message": f"Error processing query: {str(e)}",
                "processed_query": query_text,
                "original_query": query_text
            }
    
    def _process_query_typescript(self, query_text: str, location: str = "San Francisco"):
        """
        Process a query using the TypeScript implementation
        
        Args:
            query_text: The user's food query
            location: The location to search in
            
        Returns:
            Dictionary with restaurant recommendations or error message
        """
        try:
            # Run the TypeScript script with Node.js
            cmd = ["npx", "ts-node", "test-food-finder.ts", query_text, location]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the output to extract the JSON result
            output = result.stdout
            logger.debug(f"TypeScript output: {output}")
            
            # Find the JSON part in the output (after "Results:")
            results_marker = "Results:\n"
            results_pos = output.find(results_marker)
            
            if results_pos == -1:
                logger.error(f"Could not find 'Results:' marker in output: {output}")
                raise ValueError("Could not find 'Results:' marker in output")
                
            json_str = output[results_pos + len(results_marker):].strip()
            logger.debug(f"JSON string to parse: {json_str}")
            data = json.loads(json_str)
            
            # Format the response to match the expected format in app.py
            if data.get("success", False):
                # Extract query analysis if available
                query_analysis = data.get("queryAnalysis", {})
                processed_query = query_analysis.get("processedQuery", query_text) if query_analysis else query_text
                
                return {
                    "success": True,
                    "restaurants": data.get("restaurants", []),
                    "message": "",
                    "processed_query": processed_query,
                    "original_query": query_text,
                    "query_analysis": query_analysis  # Include the full query analysis
                }
            else:
                return {
                    "success": False,
                    "restaurants": [],
                    "message": data.get("message", "Unknown error"),
                    "processed_query": query_text,
                    "original_query": query_text
                }
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running TypeScript: {e.stderr}")
            return {
                "success": False,
                "restaurants": [],
                "message": f"Error running TypeScript: {e.stderr}",
                "processed_query": query_text,
                "original_query": query_text
            }
        except Exception as e:
            logger.error(f"Error processing TypeScript result: {str(e)}")
            return {
                "success": False,
                "restaurants": [],
                "message": f"Error processing TypeScript result: {str(e)}",
                "processed_query": query_text,
                "original_query": query_text
            }

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = FoodAgent()
        result = await agent.process_query("vegetarian Indian food")
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())
