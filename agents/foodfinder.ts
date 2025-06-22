import { LettaClient } from '@letta-ai/letta-client';
import { searchRestaurants } from '../tools/places';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Initialize Letta client with production API URL
const client = new LettaClient({
  baseUrl: process.env.LETTA_API_URL || "https://api.letta.ai", // Production Letta API
  token: process.env.LETTA_API_KEY || '',
});

console.log('Letta client initialized with API key');




/**
 * Agent system definition and prompts
 */
interface AgentAnalysis {
  cuisine: string | null;
  pricePreference: 'low' | 'medium' | 'high' | null;
  dietaryRestrictions: string[] | null;
  occasion: string | null;
  sortBy: 'price_low_to_high' | 'price_high_to_low' | 'rating' | null;
  searchQuery: string;
  reasoning: string;
}

// Define the agent system prompt
const FOOD_AGENT_SYSTEM_PROMPT = `You are a food discovery assistant that helps international students find restaurants.

Your task is to analyze the user's query and extract important details like:
1. Type of cuisine or food they're looking for
2. Price preferences (cheap, expensive, budget-friendly, etc.)
3. Dietary restrictions or preferences (vegetarian, vegan, gluten-free, etc.)
4. Mood or occasion (romantic, casual, quick, etc.)
5. Any sorting preferences (by price, rating, etc.)

Return your analysis as a structured JSON object with these fields:
- cuisine: The type of cuisine or food requested
- pricePreference: Any price preferences mentioned (low, medium, high, or null if not specified)
- dietaryRestrictions: Any dietary restrictions mentioned (array of strings)
- occasion: The mood or occasion mentioned (romantic, casual, quick, etc.)
- sortBy: What to sort results by (price_low_to_high, price_high_to_low, rating, or null)
- searchQuery: An optimized search query to use for finding restaurants
- reasoning: A brief explanation of your analysis

Only respond with valid JSON. Do not include any other text.`;

// Cuisine types for keyword detection
const CUISINE_TYPES = [
  'indian', 'italian', 'mexican', 'chinese', 'japanese', 'thai', 'vietnamese',
  'french', 'greek', 'mediterranean', 'american', 'korean', 'middle eastern',
  'ethiopian', 'spanish', 'german', 'brazilian', 'cuban', 'turkish', 'lebanese',
  'peruvian', 'filipino', 'russian', 'british', 'cajun', 'soul food', 'irish',
  'jamaican', 'moroccan', 'nepalese', 'pakistani', 'portuguese', 'swedish',
  'hawaiian', 'indonesian', 'malaysian', 'afghan', 'argentinian', 'australian',
  'belgian', 'caribbean', 'colombian', 'dominican', 'egyptian', 'hungarian',
  'israeli', 'polish', 'romanian', 'singaporean', 'taiwanese', 'tibetan', 'ukrainian'
];

// Dietary restrictions for keyword detection
const DIETARY_TERMS = [
  'vegetarian', 'vegan', 'gluten-free', 'gluten free', 'dairy-free', 'dairy free',
  'nut-free', 'nut free', 'halal', 'kosher', 'organic', 'pescatarian', 'keto',
  'paleo', 'low carb', 'low-carb', 'sugar-free', 'sugar free', 'soy-free', 'soy free',
  'egg-free', 'egg free', 'shellfish-free', 'shellfish free', 'wheat-free', 'wheat free'
];

// Occasion terms for keyword detection
const OCCASION_TERMS = {
  'romantic': ['romantic', 'date night', 'anniversary', 'intimate'],
  'casual': ['casual', 'relaxed', 'chill', 'laid back', 'laid-back', 'informal'],
  'quick': ['quick', 'fast', 'rapid', 'speedy', 'express', 'quick bite'],
  'family': ['family', 'kid friendly', 'kid-friendly', 'children', 'family-friendly'],
  'business': ['business', 'meeting', 'professional', 'formal', 'corporate'],
  'group': ['group', 'large party', 'team', 'gathering', 'get-together', 'get together'],
  'outdoor': ['outdoor', 'patio', 'terrace', 'al fresco', 'garden', 'rooftop']
};


/**
 * Food discovery assistant that helps international students find restaurants in San Francisco
 * @param query The user's food query (e.g., "I want spicy Indian food")
 * @param location The location to search in (default: "San Francisco")
 * @returns Restaurant recommendations
 */
export async function findFood(query: string, location: string = "San Francisco") {
  try {
    console.log(`Searching for "${query}" in ${location}...`);
    
    // Analyze the query using our agent approach
    let analysisResult: AgentAnalysis | null = null;
    
    try {
      // First try to use the Letta agent for analysis
      console.log('Analyzing query with Letta agent...');
      
      // Create a chat completion request to analyze the query
      // This is where we would use Letta's chat completions API
      // For now, we'll use a simpler approach since we're still figuring out the exact API
      
      // Extract cuisine type using our enhanced keyword detection
      const queryLower = query.toLowerCase();
      let cuisine: string | null = null;
      
      for (const type of CUISINE_TYPES) {
        if (queryLower.includes(type)) {
          cuisine = type;
          break;
        }
      }
      
      // Extract dietary restrictions
      const dietaryRestrictions: string[] = [];
      for (const term of DIETARY_TERMS) {
        if (queryLower.includes(term)) {
          dietaryRestrictions.push(term);
        }
      }
      
      // Extract occasion/mood
      let occasion: string | null = null;
      for (const [key, terms] of Object.entries(OCCASION_TERMS)) {
        for (const term of terms) {
          if (queryLower.includes(term)) {
            occasion = key;
            break;
          }
        }
        if (occasion) break;
      }
      
      // Determine price preference and sorting
      let sortBy: 'price_low_to_high' | 'price_high_to_low' | 'rating' | null = null;
      let pricePreference: 'low' | 'medium' | 'high' | null = null;
      let searchQuery = query;
      
      // Check for price-related keywords with negation handling
      // First check for negated expressions
      if (queryLower.includes('not too expensive') || queryLower.includes('not very expensive') ||
          queryLower.includes('not expensive') || queryLower.includes('not high-end')) {
        sortBy = 'price_low_to_high';
        pricePreference = 'medium'; // Not expensive usually means medium price range
        // Remove price qualifiers from search query for better results
        searchQuery = query.replace(/\b(not too expensive|not very expensive|not expensive|not high-end)\b/gi, '').trim();
      } 
      // Then check for positive expressions
      else if (queryLower.includes('cheap') || queryLower.includes('inexpensive') || 
          queryLower.includes('budget') || queryLower.includes('affordable') || 
          queryLower.includes('cheapest')) {
        sortBy = 'price_low_to_high';
        pricePreference = 'low';
        // Remove price qualifiers from search query for better results
        searchQuery = query.replace(/\b(cheap|inexpensive|budget|affordable|cheapest)\b/gi, '').trim();
      } else if (queryLower.includes('expensive') || queryLower.includes('fancy') || 
                 queryLower.includes('high-end') || queryLower.includes('luxury')) {
        sortBy = 'price_high_to_low';
        pricePreference = 'high';
        // Remove price qualifiers from search query for better results
        searchQuery = query.replace(/\b(expensive|fancy|high-end|luxury)\b/gi, '').trim();
      } else if (queryLower.includes('moderate') || queryLower.includes('mid-range') || 
                 queryLower.includes('medium priced')) {
        pricePreference = 'medium';
        sortBy = 'price_low_to_high'; // Default sorting for medium price
        // Remove price qualifiers from search query for better results
        searchQuery = query.replace(/\b(moderate|mid-range|medium priced)\b/gi, '').trim();
      } else if (queryLower.includes('best rated') || queryLower.includes('top rated') || 
                 queryLower.includes('highest rated')) {
        sortBy = 'rating';
        // Remove rating qualifiers from search query for better results
        searchQuery = query.replace(/\b(best rated|top rated|highest rated)\b/gi, '').trim();
      }
      
      // If search query became too short after removing qualifiers, use original
      if (searchQuery.length < 3) {
        searchQuery = query;
      }
      
      // Create a structured analysis result
      analysisResult = {
        cuisine,
        pricePreference,
        dietaryRestrictions: dietaryRestrictions.length > 0 ? dietaryRestrictions : null,
        occasion,
        sortBy,
        searchQuery,
        reasoning: `Analyzed query "${query}" and identified${cuisine ? ` cuisine type: ${cuisine},` : ''}
          ${pricePreference ? ` price preference: ${pricePreference},` : ''}
          ${dietaryRestrictions.length > 0 ? ` dietary restrictions: ${dietaryRestrictions.join(', ')},` : ''}
          ${occasion ? ` occasion: ${occasion},` : ''}
          ${sortBy ? ` sorting preference: ${sortBy}` : ''}`
      };
      
      console.log('Query analysis:', JSON.stringify(analysisResult, null, 2));
      
    } catch (error) {
      console.error('Error in agent analysis:', error);
      // If agent analysis fails, we'll fall back to basic keyword matching
      // This is already handled since analysisResult will be null
    }
    
    // If we don't have an analysis result (e.g., if agent analysis failed),
    // use a simple fallback that just passes the query through
    if (!analysisResult) {
      analysisResult = {
        cuisine: null,
        pricePreference: null,
        dietaryRestrictions: null,
        occasion: null,
        sortBy: null,
        searchQuery: query,
        reasoning: 'Using original query without analysis due to agent error.'
      };
    }
    
    // Get restaurant results using the optimized search query
    const results = await searchRestaurants(analysisResult.searchQuery, location);
    
    // Apply any additional sorting or filtering based on analysis
    if (results.success && results.restaurants && results.restaurants.length > 0) {
      // Apply sorting based on the analysis
      if (analysisResult.sortBy === "price_low_to_high") {
        results.restaurants.sort((a, b) => {
          const priceA = a.price_level || 999; // Default to high if price_level is missing
          const priceB = b.price_level || 999;
          return priceA - priceB;
        });
      } else if (analysisResult.sortBy === "price_high_to_low") {
        results.restaurants.sort((a, b) => {
          const priceA = a.price_level || 0; // Default to low if price_level is missing
          const priceB = b.price_level || 0;
          return priceB - priceA;
        });
      } else if (analysisResult.sortBy === "rating") {
        results.restaurants.sort((a, b) => (b.rating || 0) - (a.rating || 0));
      }
      
      // Apply dietary filtering if specified
      if (analysisResult.dietaryRestrictions && analysisResult.dietaryRestrictions.length > 0) {
        // Note: This is a placeholder. In a real implementation, we would need more
        // sophisticated filtering based on restaurant details or additional API calls
        console.log(`Would filter for dietary restrictions: ${analysisResult.dietaryRestrictions.join(', ')}`);
      }
    }
    
    // Add the query analysis to the results
    return {
      ...results,
      queryAnalysis: {
        originalQuery: query,
        processedQuery: analysisResult.searchQuery,
        cuisine: analysisResult.cuisine,
        pricePreference: analysisResult.pricePreference,
        dietaryRestrictions: analysisResult.dietaryRestrictions,
        occasion: analysisResult.occasion,
        sortBy: analysisResult.sortBy,
        reasoning: analysisResult.reasoning
      }
    };
  } catch (error) {
    console.error('Error in food finder:', error);
    return { 
      success: false, 
      message: `Error processing your request: ${error instanceof Error ? error.message : String(error)}` 
    };
  }
}
