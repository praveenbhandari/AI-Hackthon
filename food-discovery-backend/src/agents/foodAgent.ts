import { model } from '../config/gemini';
import { googlePlacesApi, googlePlacesConfig } from '../config/places';
import { yelpApi, yelpConfig } from '../config/yelp';
import { AxiosInstance } from 'axios';
import supabase from '../config/supabase';
import { QueryParams, Restaurant, UserPreference, PriceRange } from '../types';

/**
 * FoodAgent - Main agent class for reasoning about food discovery requests
 * Implements a Mastra-like approach for agent reasoning
 */
class FoodAgent {
  /**
   * Parse natural language query to extract structured parameters
   * @param query - Natural language query from user
   * @returns Structured query parameters
   */
  async parseQuery(query: string): Promise<QueryParams> {
    try {
      console.log('Parsing query:', query);
      
      // Prompt for Gemini to extract structured information
      const prompt = `
        Extract the following information from this food query. 
        Return a valid JSON object with these fields (leave empty if not mentioned):
        - cuisine: The type of food/cuisine mentioned
        - priceLevel: Price level (0=free, 1=inexpensive, 2=moderate, 3=expensive, 4=very expensive)
        - location: Any location or neighborhood mentioned
        - openNow: Whether the user wants places open now (true/false)
        - distance: Any distance constraints mentioned (in meters)
        - keywords: Array of other important keywords (e.g., "romantic", "outdoor seating")
        
        Query: "${query}"
        
        JSON response:
      `;

      // Call Gemini API to extract parameters
      const result = await model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      // Parse the JSON response
      const jsonStr = text.trim().replace(/```json|```/g, '').trim();
      const parsedParams = JSON.parse(jsonStr) as QueryParams;
      
      console.log('Extracted parameters:', parsedParams);
      return parsedParams;
    } catch (error) {
      console.error('Error parsing query:', error);
      // Return default empty parameters if parsing fails
      return {};
    }
  }

  /**
   * Decide which API to use based on query parameters and available data
   * @param params - Query parameters
   * @returns API choice ('google' or 'yelp')
   */
  decideApiSource(params: QueryParams): 'google' | 'yelp' {
    // Check if Yelp API is available
    if (!yelpApi) {
      console.log('Yelp API not available, using Google Places API');
      return 'google';
    }
    
    // Default to Google Places as primary source
    let useGoogle = true;
    
    // Use Yelp as fallback in specific cases:
    // 1. If looking for very specific cuisine types that might be better covered by Yelp
    // 2. If price level is a critical factor (Yelp has good price filtering)
    if (
      (params.cuisine && params.priceLevel !== undefined) ||
      (params.keywords && params.keywords.some(k => 
        ['romantic', 'ambiance', 'atmosphere', 'date'].includes(k.toLowerCase())))
    ) {
      useGoogle = false;
    }
    
    return useGoogle ? 'google' : 'yelp';
  }

  /**
   * Search for restaurants using Google Places API
   * @param params - Query parameters
   * @returns List of restaurants
   */
  async searchGooglePlaces(params: QueryParams): Promise<Restaurant[]> {
    try {
      // Build query parameters for Google Places API
      const queryParams: any = {
        type: 'restaurant',
      };
      
      // Add location if provided (default to San Francisco downtown if not specified)
      if (params.location) {
        queryParams.query = `${params.cuisine || ''} restaurant in ${params.location}`;
      } else {
        queryParams.query = `${params.cuisine || ''} restaurant in San Francisco`;
      }
      
      // Add open now parameter if specified
      if (params.openNow) {
        queryParams.opennow = true;
      }
      
      // Add price level if specified
      if (params.priceLevel !== undefined) {
        queryParams.minprice = params.priceLevel;
        queryParams.maxprice = params.priceLevel;
      }
      
      // Add radius if distance is specified (max 50000 meters)
      if (params.distance) {
        queryParams.radius = Math.min(params.distance, 50000);
      }
      
      // Call Google Places API
      const response = await googlePlacesApi.get(googlePlacesConfig.textSearchUrl, {
        params: queryParams
      });
      
      // Transform results to our Restaurant type
      const results = response.data.results || [];
      return results.map((place: any): Restaurant => ({
        id: place.place_id,
        name: place.name,
        address: place.formatted_address || place.vicinity,
        priceLevel: place.price_level,
        isOpen: place.opening_hours?.open_now,
        rating: place.rating,
        userRatingsTotal: place.user_ratings_total,
        photos: place.photos?.map((photo: any) => 
          `${googlePlacesConfig.baseUrl}${googlePlacesConfig.photoUrl}?photoreference=${photo.photo_reference}&maxwidth=400&key=${googlePlacesConfig.apiKey}`
        ),
        coordinates: place.geometry?.location,
      }));
    } catch (error) {
      console.error('Error searching Google Places:', error);
      return [];
    }
  }

  /**
   * Search for restaurants using Yelp API (fallback)
   * @param params - Query parameters
   * @returns List of restaurants
   */
  async searchYelp(params: QueryParams): Promise<Restaurant[]> {
    try {
      // Check if Yelp API is available
      if (!yelpApi) {
        console.warn('Yelp API not available, falling back to Google Places API');
        return this.searchGooglePlaces(params);
      }
      
      // Build query parameters for Yelp API
      const queryParams: any = {};
      
      // Add cuisine if provided
      if (params.cuisine) {
        queryParams.term = params.cuisine;
      } else {
        queryParams.term = 'restaurant';
      }
      
      // Add location if provided (default to San Francisco if not specified)
      if (params.location) {
        queryParams.location = params.location;
      } else {
        queryParams.location = 'San Francisco';
      }
      
      // Add open now parameter if specified
      if (params.openNow) {
        queryParams.open_now = true;
      }
      
      // Add price level if specified (Yelp uses 1-4 scale as strings)
      if (params.priceLevel !== undefined) {
        // Convert Google's 0-4 scale to Yelp's 1-4 scale
        const yelpPrice = Math.max(1, Math.min(4, params.priceLevel + 1));
        queryParams.price = yelpPrice.toString();
      }
      
      // Add radius if distance is specified (max 40000 meters for Yelp)
      if (params.distance) {
        queryParams.radius = Math.min(params.distance, 40000);
      }
      
      // Make the API request
      const response = await yelpApi.get(yelpConfig.businessSearchUrl, {
        params: queryParams
      });
      
      // Transform Yelp response to our Restaurant format
      const restaurants: Restaurant[] = response.data.businesses.map((business: any) => ({
        id: business.id,
        name: business.name,
        address: business.location.address1,
        location: {
          lat: business.coordinates.latitude,
          lng: business.coordinates.longitude
        },
        priceLevel: business.price ? business.price.length : 2, // Convert Yelp's '$' format to number
        isOpen: business.is_closed === false,
        rating: business.rating,
        photos: business.image_url ? [business.image_url] : [],
        cuisine: business.categories?.map((cat: any) => cat.title).join(', ') || '',
        phoneNumber: business.phone,
        website: business.url
      }));
      
      return restaurants;
    } catch (error) {
      console.error('Error searching Yelp:', error);
      // Fall back to Google Places API if Yelp fails
      console.log('Falling back to Google Places API');
      return this.searchGooglePlaces(params);
    }
  }

  /**
   * Rank and filter restaurants based on user preferences
   * @param restaurants - List of restaurants to rank
   * @param userId - User ID to get preferences for
   * @returns Ranked and filtered list of restaurants
   */
  async rankAndFilterByPreferences(
    restaurants: Restaurant[], 
    userId: string
  ): Promise<Restaurant[]> {
    try {
      // Get user preferences from Supabase
      const { data: preferences, error } = await supabase
        .from('preferences')
        .select('*')
        .eq('userId', userId)
        .single();
      
      if (error || !preferences) {
        console.log('No preferences found, returning original ranking');
        return restaurants;
      }
      
      const userPrefs = preferences as unknown as UserPreference;
      
      // Score each restaurant based on how well it matches user preferences
      const scoredRestaurants = restaurants.map(restaurant => {
        let score = 0;
        
        // Check if restaurant is in user's favorites
        if (userPrefs.favoriteRestaurants?.includes(restaurant.id)) {
          score += 10;
        }
        
        // Check if restaurant is in user's avoid list
        if (userPrefs.avoidRestaurants?.includes(restaurant.id)) {
          score -= 20;
        }
        
        // Check if restaurant matches cuisine preferences
        if (restaurant.cuisine && userPrefs.cuisinePreferences) {
          for (const cuisine of restaurant.cuisine) {
            if (userPrefs.cuisinePreferences.includes(cuisine)) {
              score += 5;
            }
          }
        }
        
        // Check if price level matches user's preferred range
        if (restaurant.priceLevel !== undefined && 
            userPrefs.priceRange !== undefined &&
            restaurant.priceLevel === userPrefs.priceRange) {
          score += 3;
        }
        
        return { restaurant, score };
      });
      
      // Sort by score (descending) and filter out negative scores
      return scoredRestaurants
        .filter(item => item.score >= 0)
        .sort((a, b) => b.score - a.score)
        .map(item => item.restaurant);
    } catch (error) {
      console.error('Error ranking restaurants by preferences:', error);
      return restaurants;
    }
  }

  /**
   * Process a food discovery query end-to-end
   * @param query - Natural language query
   * @param userId - User ID for preferences
   * @returns Processed restaurant recommendations
   */
  async processQuery(query: string, userId?: string): Promise<Restaurant[]> {
    try {
      console.log(`Processing query: "${query}" for user: ${userId || 'anonymous'}`);
      
      // Step 1: Parse the natural language query
      const queryParams = await this.parseQuery(query);
      console.log('Parsed query parameters:', queryParams);
      
      // Step 2: Decide which API to use
      const apiSource = this.decideApiSource(queryParams);
      console.log(`Selected API source: ${apiSource}`);
      
      // Step 3: Search for restaurants using the chosen API
      let restaurants: Restaurant[];
      if (apiSource === 'google') {
        restaurants = await this.searchGooglePlaces(queryParams);
      } else {
        // If Yelp API is not available, this will fall back to Google Places API
        restaurants = await this.searchYelp(queryParams);
      }
      
      console.log(`Found ${restaurants.length} restaurants before preference filtering`);
      
      // Step 4: If userId is provided, rank and filter based on preferences
      if (userId) {
        restaurants = await this.rankAndFilterByPreferences(restaurants, userId);
        console.log(`Filtered to ${restaurants.length} restaurants after applying user preferences`);
      }
      
      return restaurants;
    } catch (error) {
      console.error('Error processing query:', error);
      return [];
    }
  }

  /**
   * Generate proactive suggestions based on time, location, and user preferences
   * @param userId - User ID
   * @param location - Current location
   * @param time - Current time
   * @returns Suggested restaurants
   */
  async generateSuggestions(
    userId: string, 
    location?: { lat: number; lng: number }, 
    time?: Date
  ): Promise<Restaurant[]> {
    try {
      // Get current time if not provided
      const currentTime = time || new Date();
      const currentHour = currentTime.getHours();
      
      // Get user preferences
      const { data: preferences, error } = await supabase
        .from('preferences')
        .select('*')
        .eq('userId', userId)
        .single();
      
      if (error) {
        console.error('Error fetching user preferences:', error);
        return [];
      }
      
      const userPrefs = preferences as unknown as UserPreference;
      
      // Build query parameters based on time of day and preferences
      const queryParams: QueryParams = {
        openNow: true,
      };
      
      // Add location if provided
      if (location) {
        queryParams.location = `${location.lat},${location.lng}`;
        queryParams.distance = 2000; // 2km radius
      }
      
      // Add price range from user preferences
      if (userPrefs.priceRange !== undefined) {
        queryParams.priceLevel = userPrefs.priceRange;
      }
      
      // Add cuisine based on time of day and user preferences
      if (userPrefs.cuisinePreferences && userPrefs.cuisinePreferences.length > 0) {
        // Select a random cuisine from user's preferences
        const randomIndex = Math.floor(Math.random() * userPrefs.cuisinePreferences.length);
        queryParams.cuisine = userPrefs.cuisinePreferences[randomIndex];
      } else {
        // Default suggestions based on time of day
        if (currentHour >= 6 && currentHour < 11) {
          queryParams.cuisine = 'breakfast';
        } else if (currentHour >= 11 && currentHour < 15) {
          queryParams.cuisine = 'lunch';
        } else if (currentHour >= 17 && currentHour < 22) {
          queryParams.cuisine = 'dinner';
        } else {
          queryParams.cuisine = 'late night';
        }
      }
      
      // Search for restaurants using Google Places API
      const restaurants = await this.searchGooglePlaces(queryParams);
      
      // Rank and filter based on user preferences
      return this.rankAndFilterByPreferences(restaurants, userId);
    } catch (error) {
      console.error('Error generating suggestions:', error);
      return [];
    }
  }
}

export default new FoodAgent();
