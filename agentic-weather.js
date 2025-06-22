// Agentic weather agent using Letta for orchestration and Gemini for recommendations
const fs = require('fs');
const path = require('path');
const https = require('https');

// Read the .env file manually
function loadEnvFile() {
  const envPath = path.join(__dirname, '.env');
  try {
    const content = fs.readFileSync(envPath, 'utf8');
    const lines = content.split('\n');
    const env = {};
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      if (trimmedLine && !trimmedLine.startsWith('#')) {
        const equalsPos = trimmedLine.indexOf('=');
        if (equalsPos > 0) {
          const key = trimmedLine.substring(0, equalsPos);
          const value = trimmedLine.substring(equalsPos + 1);
          env[key] = value;
        }
      }
    }
    
    return env;
  } catch (error) {
    console.error('Error loading .env file:', error);
    return {};
  }
}

// Load environment variables
const env = loadEnvFile();
console.log('Loaded environment variables:');
for (const key in env) {
  if (key.includes('KEY')) {
    console.log(`${key}: ${env[key] ? '[SET]' : '[NOT SET]'}`);
  } else {
    console.log(`${key}: ${env[key]}`);
  }
}

// Load required libraries
const { GoogleGenerativeAI } = require('@google/generative-ai');
const { LettaClient } = require('@letta-ai/letta-client');

// Initialize API clients
const geminiModel = new GoogleGenerativeAI(env.GOOGLE_GEMINI_API_KEY || env.GEMINI_API_KEY || '').getGenerativeModel({ model: 'gemini-1.5-pro' });

// Initialize Letta client if API key is available
let lettaClient = null;
let lettaAgentId = null; // Store agent ID if we create one

if (env.LETTA_API_KEY) {
  try {
    lettaClient = new LettaClient({
      baseUrl: env.LETTA_API_URL || 'https://api.letta.ai',
      token: env.LETTA_API_KEY
    });
    console.log('Letta client initialized successfully');
    
    // Debug available methods and structure
    console.log('Available Letta client methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(lettaClient)));
    
    // Check if agents object exists and log its structure
    if (lettaClient.agents) {
      console.log('Letta agents object methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(lettaClient.agents)));
    }
    
    // Check if runs object exists and log its structure
    if (lettaClient.runs) {
      console.log('Letta runs object methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(lettaClient.runs)));
    }
  } catch (error) {
    console.error('Error initializing Letta client:', error);
    lettaClient = null;
  }
}

// Weather API functions
async function getWeather(location) {
  return new Promise((resolve, reject) => {
    const apiKey = env.OPENWEATHER_API_KEY;
    if (!apiKey) {
      return reject(new Error('OpenWeatherMap API key not found in .env file'));
    }
    
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(location)}&appid=${apiKey}&units=metric`;
    console.log(`Weather API URL: ${url}`);
    console.log(`Requesting weather data for location: ${location}`);
    
    https.get(url, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            console.log(`Raw weather API response: ${data}`);
            const weatherData = JSON.parse(data);
            console.log(`Weather data for ${weatherData.name}, ${weatherData.sys.country}:`);
            console.log(`- Temperature: ${weatherData.main.temp}°C (feels like ${weatherData.main.feels_like}°C)`);
            console.log(`- Description: ${weatherData.weather[0].description}`);
            console.log(`- Humidity: ${weatherData.main.humidity}%`);
            console.log(`- Wind: ${weatherData.wind.speed} m/s`);
            console.log(`- Coordinates: [${weatherData.coord.lat}, ${weatherData.coord.lon}]`);
            
            resolve({
              city: weatherData.name,
              country: weatherData.sys.country,
              temperature: weatherData.main.temp,
              feels_like: weatherData.main.feels_like,
              description: weatherData.weather[0].description,
              humidity: weatherData.main.humidity,
              wind_speed: weatherData.wind.speed,
              icon: weatherData.weather[0].icon
            });
          } catch (error) {
            console.error(`Error parsing weather data: ${error.message}`);
            reject(new Error(`Error parsing weather data: ${error.message}`));
          }
        } else {
          console.error(`Weather API error: ${res.statusCode} - ${data}`);
          reject(new Error(`Weather API error: ${res.statusCode} - ${data}`));
        }
      });
    }).on('error', (error) => {
      console.error(`Request error: ${error.message}`);
      reject(new Error(`Request error: ${error.message}`));
    });
  });
}

// Get forecast data
async function getForecast(location) {
  return new Promise((resolve, reject) => {
    const apiKey = env.OPENWEATHER_API_KEY;
    if (!apiKey) {
      return reject(new Error('OpenWeatherMap API key not found in .env file'));
    }
    
    const url = `https://api.openweathermap.org/data/2.5/forecast?q=${encodeURIComponent(location)}&appid=${apiKey}&units=metric`;
    
    https.get(url, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const forecastData = JSON.parse(data);
            
            // Group forecast by day and get daily data
            const dailyForecasts = [];
            const dailyMap = new Map();
            
            forecastData.list.forEach((item) => {
              const date = new Date(item.dt * 1000).toISOString().split('T')[0];
              
              if (!dailyMap.has(date)) {
                dailyMap.set(date, {
                  date,
                  temperature: {
                    min: item.main.temp_min,
                    max: item.main.temp_max
                  },
                  description: item.weather[0].description,
                  icon: item.weather[0].icon,
                  precipitation_probability: item.pop * 100
                });
              } else {
                const existing = dailyMap.get(date);
                existing.temperature.min = Math.min(existing.temperature.min, item.main.temp_min);
                existing.temperature.max = Math.max(existing.temperature.max, item.main.temp_max);
              }
            });
            
            // Convert map to array and take first 5 days
            dailyMap.forEach((value) => {
              dailyForecasts.push(value);
            });
            
            resolve(dailyForecasts.slice(0, 5));
          } catch (error) {
            reject(new Error(`Error parsing forecast data: ${error.message}`));
          }
        } else {
          reject(new Error(`Forecast API error: ${res.statusCode} - ${data}`));
        }
      });
    }).on('error', (error) => {
      reject(new Error(`Request error: ${error.message}`));
    });
  });
}

// Use Gemini API directly for clothing recommendations
async function getGeminiRecommendation(weatherData) {
  console.log('Using Gemini API for clothing recommendations...');
  
  try {
    // Format the weather data for the prompt
    const prompt = `
      I need clothing recommendations based on the following weather data:
      
      Location: ${weatherData.city}, ${weatherData.country}
      Current time: ${weatherData.currentTime}
      Time of day: ${weatherData.timeOfDay}
      Temperature: ${weatherData.temperature}°C (feels like ${weatherData.feels_like}°C)
      Weather condition: ${weatherData.description}
      Humidity: ${weatherData.humidity}%
      Wind speed: ${weatherData.wind_speed} m/s
      ${weatherData.rain ? `Rain: ${weatherData.rain} mm in the last hour` : ''}
      ${weatherData.snow ? `Snow: ${weatherData.snow} mm in the last hour` : ''}
      
      Forecast for the next few days:
      ${weatherData.forecast ? weatherData.forecast.map(day => `
        Date: ${day.date}
        Min temp: ${day.temperature.min}°C
        Max temp: ${day.temperature.max}°C
        Conditions: ${day.description}
        Precipitation probability: ${day.precipitation_probability}%
      `).join('') : 'No forecast data available'}
      
      Please provide detailed clothing recommendations in JSON format with the following structure:
      {
        "recommendation": {
          "top": "[specific recommendation for upper body clothing]",
          "bottom": "[specific recommendation for lower body clothing]",
          "outerwear": "[specific recommendation for jacket/coat if needed]",
          "accessories": ["list", "of", "recommended", "accessories"],
          "footwear": "[specific recommendation for shoes]",
          "additional_tips": ["list", "of", "helpful", "tips"]
        },
        "reasoning": "[detailed explanation for your recommendations considering temperature, weather conditions, time of day, etc.]"
      }
      
      Make sure the recommendations are appropriate for the current weather conditions and time of day.
      Be specific about the clothing items (e.g., "cotton t-shirt" instead of just "t-shirt").
      IMPORTANT: Return ONLY valid JSON that can be parsed directly.
    `;
    
    // Call Gemini API using the global geminiModel
    const result = await geminiModel.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    // Extract JSON from response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      console.warn('Could not extract JSON from Gemini response, falling back');
      return generateSimpleFallbackRecommendation(weatherData);
    }
    
    try {
      const data = JSON.parse(jsonMatch[0]);
      console.log('Gemini API response received and parsed successfully');
      
      // Validate the response structure
      if (!data.recommendation || !data.reasoning) {
        console.warn('Gemini response missing required fields, falling back');
        return generateSimpleFallbackRecommendation(weatherData);
      }
      
      return data;
    } catch (parseError) {
      console.error('Error parsing Gemini response:', parseError);
      return generateSimpleFallbackRecommendation(weatherData);
    }
  } catch (error) {
    console.error('Error with Gemini API:', error);
    return generateSimpleFallbackRecommendation(weatherData);
  }
}

// Simple fallback if Gemini API is unavailable
function generateSimpleFallbackRecommendation(weatherData) {
  // Create basic recommendation based on temperature and conditions
  const temp = weatherData.temperature;
  const timeOfDay = weatherData.timeOfDay || 'afternoon';
  const description = weatherData.description || '';
  const windSpeed = weatherData.wind_speed || 0;
  
  // Create recommendation object with dynamic generation
  const recommendation = {
    top: '',
    bottom: '',
    outerwear: '',
    accessories: [],
    footwear: '',
    additional_tips: []
  };
  
  // Temperature-based top recommendation
  if (temp < 5) {
    recommendation.top = 'Warm layers including thermal shirt and heavy sweater';
  } else if (temp < 15) {
    recommendation.top = 'Long-sleeve shirt or light sweater';
  } else if (temp < 25) {
    recommendation.top = 'T-shirt or short-sleeve shirt';
  } else {
    recommendation.top = 'Light t-shirt or tank top';
  }
  
  // Temperature-based bottom recommendation
  if (temp < 5) {
    recommendation.bottom = 'Thermal pants and heavy jeans or wool pants';
  } else if (temp < 15) {
    recommendation.bottom = 'Jeans or casual pants';
  } else if (temp < 25) {
    recommendation.bottom = 'Light pants or shorts';
  } else {
    recommendation.bottom = 'Shorts or light skirt';
  }
  
  // Temperature and time-based outerwear
  if (temp < 5) {
    recommendation.outerwear = 'Heavy winter coat';
  } else if (temp < 15) {
    recommendation.outerwear = (timeOfDay === 'night' || timeOfDay === 'evening') ? 
      'Warm jacket or coat' : 'Light to medium jacket';
  } else if (temp < 25) {
    recommendation.outerwear = (timeOfDay === 'night' || timeOfDay === 'evening') ? 
      'Light jacket' : 'Optional light jacket';
  } else {
    recommendation.outerwear = 'None needed';
  }
  
  // Weather condition based accessories
  if (description.includes('rain') || description.includes('drizzle')) {
    recommendation.accessories.push('Umbrella');
  }
  
  if (temp < 10) {
    recommendation.accessories.push('Hat', 'Gloves');
  }
  
  if (description.includes('clear') && temp > 15) {
    recommendation.accessories.push('Sunglasses');
  }
  
  if (windSpeed > 5 && !recommendation.accessories.includes('Hat')) {
    recommendation.accessories.push('Hat to protect from wind');
  }
  
  // Footwear
  if (description.includes('rain')) {
    recommendation.footwear = 'Waterproof shoes or boots';
  } else if (description.includes('snow')) {
    recommendation.footwear = 'Waterproof snow boots with good traction';
  } else if (temp < 10) {
    recommendation.footwear = 'Closed shoes or boots';
  } else if (temp < 25) {
    recommendation.footwear = 'Sneakers or casual shoes';
  } else {
    recommendation.footwear = 'Sandals or breathable shoes';
  }
  
  // Additional tips based on conditions
  if (temp > 25) {
    recommendation.additional_tips.push('Stay hydrated');
  }
  
  if (timeOfDay === 'morning') {
    recommendation.additional_tips.push('Layer clothing as temperature may change throughout the day');
  } else if (timeOfDay === 'night') {
    recommendation.additional_tips.push('Dress warmer than daytime as temperatures are lower at night');
  }
  
  if (description.includes('rain')) {
    recommendation.additional_tips.push('Bring waterproof protection');
  }
  
  if (description.includes('snow')) {
    recommendation.additional_tips.push('Layer clothing for better insulation');
    recommendation.additional_tips.push('Wear waterproof outer layers');
  }
  
  if (windSpeed > 5) {
    recommendation.additional_tips.push('Wear windproof outer layers');
  }
  
  // Generate simple reasoning
  const reasoning = `Based on the current weather in ${weatherData.city} (${temp}°C, ${description}) during the ${timeOfDay}, I recommend appropriate clothing for these conditions. Consider the forecast and adjust as needed.`;
  
  return {
    recommendation,
    reasoning
  };
}

// Generate reasoning for the clothing recommendations
function generateReasoning(weatherData, recommendation) {
  const timeOfDay = weatherData.timeOfDay || 'afternoon';
  
  let reasoning = `Based on the current weather in ${weatherData.city} (${weatherData.temperature}°C, ${weatherData.description}) during the ${timeOfDay}, `;
  
  // Temperature reasoning
  if (weatherData.temperature < 0) {
    reasoning += "it's extremely cold outside. ";
  } else if (weatherData.temperature < 10) {
    reasoning += "it's quite cold today. ";
  } else if (weatherData.temperature < 20) {
    reasoning += "it's cool but moderate. ";
  } else if (weatherData.temperature < 30) {
    reasoning += "it's warm and pleasant. ";
  } else {
    reasoning += "it's very hot today. ";
  }
  
  // Time of day specific reasoning
  if (timeOfDay === 'morning') {
    reasoning += "Since it's morning, temperatures may rise throughout the day. ";
  } else if (timeOfDay === 'afternoon') {
    reasoning += "During the afternoon, you're experiencing the warmest part of the day. ";
  } else if (timeOfDay === 'evening') {
    reasoning += "As it's evening, temperatures will likely drop as night approaches. ";
  } else if (timeOfDay === 'night') {
    reasoning += "At night, temperatures are typically cooler than during the day. ";
  }
  
  // Clothing reasoning
  reasoning += `I recommend wearing ${recommendation.top} with ${recommendation.bottom}. `;
  
  if (recommendation.outerwear && recommendation.outerwear !== 'None needed') {
    reasoning += `You should also wear ${recommendation.outerwear} for protection. `;
  }
  
  if (recommendation.accessories.length > 0) {
    reasoning += `Don't forget to bring ${recommendation.accessories.join(' and ')}. `;
  }
  
  reasoning += `For footwear, ${recommendation.footwear} would be appropriate. `;
  
  // Additional tips
  if (recommendation.additional_tips.length > 0) {
    reasoning += "Additional tips: " + recommendation.additional_tips.join('. ') + '.';
  }
      
  return reasoning;
}

// Main function to get weather recommendation
async function getWeatherRecommendation(location) {
  try {
    console.log(`Getting weather recommendation for ${location}...`);
        
    // Check if Letta client is available
    if (lettaClient) {
      try {
        console.log('Attempting to use Letta for orchestration...');
        // This is a placeholder for future Letta integration
        // Currently we'll just throw an error to trigger the fallback
        throw new Error('Letta integration not fully implemented');
      } catch (lettaError) {
        console.log('-');
        return await getWeatherRecommendationDirect(location);
      }
    } else {
      // If no Letta client, use direct API calls
      return await getWeatherRecommendationDirect(location);
    }
  } catch (error) {
    console.error('Error in weather recommendation:', error);
    return {
      success: false,
      message: `Error: ${error.message || String(error)}`,
      source: 'error'
    };
  }
}

// Direct API call function (fallback if Letta is unavailable)
async function getWeatherRecommendationDirect(location) {
  try {
    console.log(`Getting weather recommendation directly for ${location}...`);
    
    // Fetch current weather
    const weatherData = await getWeather(location);
    if (!weatherData) {
      return {
        success: false,
        message: `Could not fetch weather data for ${location}`
      };
    }
    
    // Fetch forecast data
    const forecastData = await getForecast(location);
    if (forecastData) {
      weatherData.forecast = forecastData;
    }
    
    // Add time of day
    const currentTime = new Date();
    weatherData.currentTime = currentTime.toISOString();
    const hour = currentTime.getHours();
    weatherData.hour = hour;
    
    // Determine time of day
    let timeOfDay = 'afternoon';
    if (hour >= 5 && hour < 12) {
      timeOfDay = 'morning';
    } else if (hour >= 12 && hour < 17) {
      timeOfDay = 'afternoon';
    } else if (hour >= 17 && hour < 21) {
      timeOfDay = 'evening';
    } else {
      timeOfDay = 'night';
    }
    weatherData.timeOfDay = timeOfDay;
    
    // Generate clothing recommendations using Gemini
    let recommendation = null;
    let reasoning = null;
    let source = 'gemini';
    
    try {
      const geminiResult = await getGeminiRecommendation(weatherData);
      recommendation = geminiResult.recommendation;
      reasoning = geminiResult.reasoning;
    } catch (error) {
      console.error("Error with Gemini API:", error);
      console.log("Falling back to simple recommendation system...");
      
      // Use fallback if Gemini fails
      const fallbackResult = generateSimpleFallbackRecommendation(weatherData);
      recommendation = fallbackResult.recommendation;
      reasoning = fallbackResult.reasoning;
      source = 'rule-based-fallback';
    }
    
    return {
      success: true,
      weather: weatherData,
      recommendation,
      reasoning,
      source
    };
  } catch (error) {
    console.error("Error in direct weather agent:", error);
    return {
      success: false,
      message: `Error: ${error.message || String(error)}`,
      source: 'error'
    };
  }
}

// Export the function for use in other modules
module.exports = {
  getWeatherRecommendation
};

// Only run this if called directly from command line (not when imported)
if (require.main === module) {
  // Handle command line arguments
  const location = process.argv[2] || 'San Francisco';
  getWeatherRecommendation(location)
    .then(result => {
      console.log('\nResults:');
      console.log(JSON.stringify(result, null, 2));
    })
    .catch(error => {
      console.error('Unhandled error:', error);
    });
}
