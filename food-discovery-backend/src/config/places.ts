import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

// Check if the required environment variables are set
if (!process.env.GOOGLE_PLACES_API_KEY) {
  console.error('Missing Google Places API key. Please check your .env file.');
  process.exit(1);
}

// Google Places API configuration
const googlePlacesConfig = {
  apiKey: process.env.GOOGLE_PLACES_API_KEY,
  baseUrl: 'https://maps.googleapis.com/maps/api/place',
  nearbySearchUrl: '/nearbysearch/json',
  detailsUrl: '/details/json',
  photoUrl: '/photo',
  textSearchUrl: '/textsearch/json',
};

// Create an axios instance for Google Places API
const googlePlacesApi = axios.create({
  baseURL: googlePlacesConfig.baseUrl,
  params: {
    key: googlePlacesConfig.apiKey,
  },
});

export { googlePlacesConfig, googlePlacesApi };
