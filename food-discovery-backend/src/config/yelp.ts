import axios, { AxiosInstance } from 'axios';
import dotenv from 'dotenv';

dotenv.config();

// Check if the Yelp API key is set
const hasYelpApiKey = !!process.env.YELP_API_KEY;
if (!hasYelpApiKey) {
  console.warn('Yelp API key not found. Yelp API features will be disabled.');
}

// Yelp API configuration
const yelpConfig = {
  apiKey: process.env.YELP_API_KEY,
  baseUrl: 'https://api.yelp.com/v3',
  businessSearchUrl: '/businesses/search',
  businessDetailsUrl: '/businesses/',
  reviewsUrl: '/reviews',
};

// Create an axios instance for Yelp API if the API key is available
let yelpApi: AxiosInstance | null = null;
if (hasYelpApiKey) {
  yelpApi = axios.create({
    baseURL: yelpConfig.baseUrl,
    headers: {
      Authorization: `Bearer ${process.env.YELP_API_KEY}`,
      'Content-Type': 'application/json',
    },
  });
}

export { yelpConfig, yelpApi };
