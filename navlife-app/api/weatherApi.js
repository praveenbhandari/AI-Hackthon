/**
 * Weather API integration layer
 * Connects to the agentic-weather.js backend
 */

// Base URL for API calls - change this to your actual backend URL when deployed
const API_BASE_URL = 'http://localhost:9876';

/**
 * Get weather recommendation for a location
 * @param {string} location - City name
 * @returns {Promise<Object>} - Weather and clothing recommendation data
 */
export const getWeatherRecommendation = async (location) => {
  try {
    console.log(`Getting weather recommendation for ${location}...`);
    
    // Call the backend API through our server.js gateway
    try {
      const response = await fetch(`${API_BASE_URL}/api/weather/recommendation?location=${encodeURIComponent(location)}`);
      const data = await response.json();
      return data;
    } catch (fetchError) {
      console.error('Error fetching from API:', fetchError);
      console.log('Falling back to mock data...');
      
      // Fallback to mock data if API is not available
      return new Promise((resolve) => {
        setTimeout(() => {
          // Mock response based on your agentic-weather.js output format
          resolve({
            success: true,
            weather: {
              city: location,
              country: "US",
              temperature: 14.45,
              feels_like: 13.86,
              description: "clear sky",
              humidity: 73,
              wind_speed: 0.89,
              icon: "01n",
              forecast: [
                {
                  date: "2025-06-22",
                  temperature: {
                    min: 12.31,
                    max: 24.11
                  },
                  description: "clear sky",
                  icon: "01n",
                  precipitation_probability: 0
                },
                {
                  date: "2025-06-23",
                  temperature: {
                    min: 12.37,
                    max: 22.41
                  },
                  description: "clear sky",
                  icon: "01d",
                  precipitation_probability: 0
                },
                {
                  date: "2025-06-24",
                  temperature: {
                    min: 12.46,
                    max: 16.86
                  },
                  description: "clear sky",
                  icon: "01d",
                  precipitation_probability: 0
                }
              ],
              currentTime: new Date().toISOString(),
              hour: new Date().getHours(),
              timeOfDay: new Date().getHours() >= 6 && new Date().getHours() < 18 ? "day" : "night"
            },
            recommendation: {
              top: "Long-sleeved t-shirt or light sweater",
              bottom: "Jeans or chinos",
              outerwear: "Light jacket or hoodie",
              accessories: [
                "Light scarf (optional)",
                "Watch"
              ],
              footwear: "Sneakers or comfortable walking shoes",
              additional_tips: [
                "Dress in layers as temperatures will increase throughout the day.",
                "Consider a hat for sun protection during the day."
              ]
            },
            reasoning: `It's currently ${new Date().getHours() >= 6 && new Date().getHours() < 18 ? "day" : "night"} in ${location} with a temperature of 14.45°C, which feels like 13.86°C. A long-sleeved t-shirt or light sweater will provide enough warmth for the cool air. Jeans or chinos are suitable for the bottom. A light jacket or hoodie is recommended as an outer layer for extra warmth during the night and cooler morning hours.`,
            source: "gemini"
          });
        }, 1500);
      });
    }
  } catch (error) {
    console.error('Error getting weather recommendation:', error);
    return {
      success: false,
      message: error.message || 'Failed to get weather recommendation'
    };
  }
};
