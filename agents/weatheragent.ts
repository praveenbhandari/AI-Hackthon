import { LettaClient } from '@letta-ai/letta-client';
import * as fs from 'fs';
import * as path from 'path';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Function to read API keys directly from .env file
function readEnvFile() {
  try {
    const envPath = path.join(__dirname, '..', '.env');
    const envContent = fs.readFileSync(envPath, 'utf8');
    const lines = envContent.split('\n');
    const env: Record<string, string> = {};
    
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
    console.error('Error reading .env file:', error);
    return {};
  }
}

// Read environment variables directly from .env file
const env = readEnvFile();

// API keys
const WEATHER_API_KEY = env.OPENWEATHER_API_KEY || '';
const GEMINI_API_KEY = env.GEMINI_API_KEY || '';
const LETTA_API_KEY = env.LETTA_API_KEY || '';
const LETTA_API_URL = env.LETTA_API_URL || 'https://api.letta.ai';

// Initialize Letta client
const lettaClient = new LettaClient({
  baseUrl: LETTA_API_URL,
  token: LETTA_API_KEY,
});

// Initialize Gemini client
const geminiClient = new GoogleGenerativeAI(GEMINI_API_KEY);
const geminiModel = geminiClient.getGenerativeModel({ model: "gemini-pro" });

// Validate API keys
if (!WEATHER_API_KEY) {
  console.error('ERROR: OPENWEATHER_API_KEY is not set in .env file');
}

if (!GEMINI_API_KEY) {
  console.error('ERROR: GEMINI_API_KEY is not set in .env file');
}

console.log('Environment variables loaded:');
console.log('OPENWEATHER_API_KEY:', WEATHER_API_KEY ? '[SET]' : '[NOT SET]');
console.log('GEMINI_API_KEY:', GEMINI_API_KEY ? '[SET]' : '[NOT SET]');
console.log('LETTA_API_KEY:', LETTA_API_KEY ? '[SET]' : '[NOT SET]');

/**
 * Interface for weather data
 */
interface WeatherData {
  temperature: number;
  feels_like: number;
  humidity: number;
  wind_speed: number;
  description: string;
  icon: string;
  city: string;
  country: string;
  rain?: number;
  snow?: number;
  uv_index?: number;
  forecast?: ForecastData[];
}

/**
 * Interface for forecast data
 */
interface ForecastData {
  date: string;
  temperature: {
    min: number;
    max: number;
  };
  description: string;
  icon: string;
  precipitation_probability: number;
}

/**
 * Interface for clothing recommendation
 */
interface ClothingRecommendation {
  top: string;
  bottom: string;
  outerwear: string;
  accessories: string[];
  footwear: string;
  additional_tips: string[];
}

/**
 * Interface for weather agent response
 */
interface WeatherAgentResponse {
  success: boolean;
  message?: string;
  weather?: WeatherData;
  recommendation?: ClothingRecommendation;
  reasoning?: string;
}

/**
 * Fetch current weather data from OpenWeatherMap API
 * @param location Location to get weather for
 * @returns Weather data
 */
async function fetchWeatherData(location: string): Promise<WeatherData | null> {
  try {
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(
      location
    )}&appid=${WEATHER_API_KEY}&units=metric`;
    
    console.log(`Fetching weather data from: ${url.replace(WEATHER_API_KEY, 'API_KEY_HIDDEN')}`);
    
    if (!WEATHER_API_KEY) {
      throw new Error('OpenWeatherMap API key is not set');
    }
    
    const response = await fetch(url);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Weather API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    
    return {
      temperature: data.main.temp,
      feels_like: data.main.feels_like,
      humidity: data.main.humidity,
      wind_speed: data.wind.speed,
      description: data.weather[0].description,
      icon: data.weather[0].icon,
      city: data.name,
      country: data.sys.country,
      rain: data.rain ? data.rain["1h"] : 0,
      snow: data.snow ? data.snow["1h"] : 0
    };
  } catch (error) {
    console.error("Error fetching weather data:", error);
    return null;
  }
}

/**
 * Fetch forecast data from OpenWeatherMap API
 * @param location Location to get forecast for
 * @returns Forecast data for next 5 days
 */
async function fetchForecastData(location: string): Promise<ForecastData[] | null> {
  try {
    const response = await fetch(
      `https://api.openweathermap.org/data/2.5/forecast?q=${encodeURIComponent(
        location
      )}&appid=${WEATHER_API_KEY}&units=metric`
    );

    if (!response.ok) {
      throw new Error(`Forecast API error: ${response.status}`);
    }

    const data = await response.json();
    
    // Group forecast by day and get daily data
    const dailyForecasts: ForecastData[] = [];
    const dailyMap = new Map();
    
    data.list.forEach((item: any) => {
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
    
    return dailyForecasts.slice(0, 5);
  } catch (error) {
    console.error("Error fetching forecast data:", error);
    return null;
  }
}

/**
 * Generate clothing recommendations using Gemini
 * @param weatherData Weather data
 * @returns Clothing recommendations
 */
async function generateClothingRecommendations(weatherData: WeatherData): Promise<ClothingRecommendation | null> {
  try {
    const prompt = `
    You are a helpful assistant that provides clothing recommendations based on weather conditions.
    
    Current weather in ${weatherData.city}, ${weatherData.country}:
    - Temperature: ${weatherData.temperature}°C (feels like ${weatherData.feels_like}°C)
    - Conditions: ${weatherData.description}
    - Humidity: ${weatherData.humidity}%
    - Wind Speed: ${weatherData.wind_speed} m/s
    ${weatherData.rain ? `- Rain: ${weatherData.rain} mm in the last hour` : ''}
    ${weatherData.snow ? `- Snow: ${weatherData.snow} mm in the last hour` : ''}
    
    Based on these weather conditions, provide detailed clothing recommendations in JSON format with the following structure:
    {
      "top": "Recommended top clothing",
      "bottom": "Recommended bottom clothing",
      "outerwear": "Recommended outerwear if needed",
      "accessories": ["List of recommended accessories"],
      "footwear": "Recommended footwear",
      "additional_tips": ["Additional weather-specific tips"]
    }
    
    Only respond with the JSON, no additional text.
    `;

    const result = await geminiModel.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    // Extract JSON from response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    } else {
      throw new Error("Failed to parse JSON from Gemini response");
    }
  } catch (error) {
    console.error("Error generating clothing recommendations:", error);
    return null;
  }
}

/**
 * Generate reasoning for recommendations using Letta
 * @param weatherData Weather data
 * @param recommendation Clothing recommendation
 * @returns Reasoning text
 */
async function generateReasoning(weatherData: WeatherData, recommendation: ClothingRecommendation): Promise<string | null> {
  try {
    // This is a placeholder for actual Letta API call
    // In a real implementation, you would use Letta's chat completion API
    
    // For now, we'll use Gemini as a fallback
    const prompt = `
    You are a helpful assistant that explains clothing recommendations based on weather conditions.
    
    Current weather in ${weatherData.city}, ${weatherData.country}:
    - Temperature: ${weatherData.temperature}°C (feels like ${weatherData.feels_like}°C)
    - Conditions: ${weatherData.description}
    - Humidity: ${weatherData.humidity}%
    - Wind Speed: ${weatherData.wind_speed} m/s
    ${weatherData.rain ? `- Rain: ${weatherData.rain} mm in the last hour` : ''}
    ${weatherData.snow ? `- Snow: ${weatherData.snow} mm in the last hour` : ''}
    
    Clothing recommendations:
    - Top: ${recommendation.top}
    - Bottom: ${recommendation.bottom}
    - Outerwear: ${recommendation.outerwear}
    - Accessories: ${recommendation.accessories.join(', ')}
    - Footwear: ${recommendation.footwear}
    
    Please provide a detailed explanation of why these clothing choices are appropriate for the current weather conditions.
    Keep your explanation concise but informative, focusing on how these choices address the specific weather challenges.
    `;

    const result = await geminiModel.generateContent(prompt);
    const response = await result.response;
    return response.text();
  } catch (error) {
    console.error("Error generating reasoning:", error);
    return null;
  }
}

/**
 * Main function to get weather and clothing recommendations
 * @param location Location to get weather for
 * @returns Weather agent response
 */
export async function getWeatherRecommendation(location: string): Promise<WeatherAgentResponse> {
  try {
    console.log(`Getting weather recommendation for ${location}...`);
    
    // Fetch current weather
    const weatherData = await fetchWeatherData(location);
    if (!weatherData) {
      return {
        success: false,
        message: `Could not fetch weather data for ${location}`
      };
    }
    
    // Fetch forecast data
    const forecastData = await fetchForecastData(location);
    if (forecastData) {
      weatherData.forecast = forecastData;
    }
    
    // Generate clothing recommendations
    const recommendation = await generateClothingRecommendations(weatherData);
    if (!recommendation) {
      return {
        success: false,
        message: "Could not generate clothing recommendations",
        weather: weatherData
      };
    }
    
    // Generate reasoning
    const reasoning = await generateReasoning(weatherData, recommendation);
    
    return {
      success: true,
      weather: weatherData,
      recommendation,
      reasoning: reasoning || undefined
    };
  } catch (error) {
    console.error("Error in weather agent:", error);
    return {
      success: false,
      message: `Error: ${error instanceof Error ? error.message : String(error)}`
    };
  }
}

// Handle command line arguments if run directly
if (require.main === module) {
  const location = process.argv[2] || "San Francisco";
  
  getWeatherRecommendation(location)
    .then(result => {
      console.log("Results:");
      console.log(JSON.stringify(result, null, 2));
    })
    .catch(error => {
      console.error("Error:", error);
    });
}
