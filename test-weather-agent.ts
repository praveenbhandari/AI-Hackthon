import { getWeatherRecommendation } from './agents/weatheragent';

/**
 * Test script for the Weather Agent
 */
async function testWeatherAgent() {
  console.log("Testing Weather Agent...");
  
  // Get location from command line arguments or default to San Francisco
  const location = process.argv[2] || "San Francisco";
  
  console.log(`Getting weather recommendation for ${location}...`);
  
  try {
    const result = await getWeatherRecommendation(location);
    
    console.log("Results:");
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error("Error:", error);
  }
}

// Run the test
testWeatherAgent();
