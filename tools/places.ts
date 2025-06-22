import { LettaClient } from '@letta-ai/letta-client';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Define interfaces for Google Places API response
interface PlaceLocation {
  lat: number;
  lng: number;
}

interface PlaceResult {
  name: string;
  rating: number;
  formatted_address: string;
  price_level?: number;
  user_ratings_total: number;
  photos?: {
    photo_reference: string;
    height: number;
    width: number;
  }[];
  geometry?: {
    location: PlaceLocation;
  };
}

interface PlacesApiResponse {
  results: PlaceResult[];
  status: string;
}

/**
 * Search for restaurants using Google Places API
 * @param query The search query (e.g., "Italian food")
 * @param location The location to search in (e.g., "San Francisco")
 * @returns Array of restaurant information or error message
 */
export async function searchRestaurants(query: string, location: string) {
  try {
    const url = `https://maps.googleapis.com/maps/api/place/textsearch/json?query=${encodeURIComponent(query)}+in+${encodeURIComponent(location)}&key=${process.env.GOOGLE_PLACES_API_KEY}`;
    const res = await fetch(url);
    const data = await res.json() as PlacesApiResponse;

    if (!data.results || data.results.length === 0) {
      return { success: false, message: "No results found." };
    }

    // Get the API key from environment variables
    const apiKey = process.env.GOOGLE_PLACES_API_KEY;
    
    return {
      success: true,
      restaurants: data.results.slice(0, 5).map((place: PlaceResult) => {
        // Create photo URLs if available
        const photos = place.photos ? 
          place.photos.slice(0, 1).map(photo => 
            `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=${photo.photo_reference}&key=${apiKey}`
          ) : 
          ['https://via.placeholder.com/400x300?text=No+Image+Available'];
          
        return {
          name: place.name,
          rating: place.rating,
          address: place.formatted_address,
          price_level: place.price_level,
          user_ratings_total: place.user_ratings_total,
          location: place.geometry?.location || { lat: 37.7749, lng: -122.4194 },  // Default to SF coordinates if not available
          types: ['restaurant'],  // Add a default type
          photos: photos
        };
      })
    };
  } catch (error) {
    console.error('Error searching for restaurants:', error);
    return { success: false, message: `Error: ${error instanceof Error ? error.message : String(error)}` };
  }
}
