/**
 * Test script for Food Discovery API endpoints
 * Run with: npx ts-node src/utils/testEndpoints.ts
 */
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const API_URL = 'http://localhost:3000';
const TEST_USER_ID = 'test-user-123';

/**
 * Test all API endpoints
 */
const testEndpoints = async (): Promise<void> => {
  try {
    console.log('🧪 Testing Food Discovery API endpoints...');
    
    // Test health endpoint
    console.log('\n🔍 Testing health endpoint...');
    const healthResponse = await axios.get(`${API_URL}/health`);
    console.log('✅ Health endpoint response:', healthResponse.data);
    
    // Test query endpoint
    console.log('\n🔍 Testing query endpoint...');
    const queryResponse = await axios.post(`${API_URL}/query`, {
      query: 'Find a cheap Italian restaurant near Union Square',
      userId: TEST_USER_ID
    });
    console.log('✅ Query endpoint response:', queryResponse.data);
    
    // Test preferences endpoints
    console.log('\n🔍 Testing preferences endpoints...');
    
    // Save preferences
    const preferencesData = {
      userId: TEST_USER_ID,
      dietaryRestrictions: ['vegetarian'],
      cuisinePreferences: ['italian', 'indian', 'mexican'],
      priceRange: 2,
      spicyLevel: 3,
      favoriteRestaurants: [],
      avoidRestaurants: []
    };
    
    const savePrefsResponse = await axios.post(`${API_URL}/preferences`, preferencesData);
    console.log('✅ Save preferences response:', savePrefsResponse.data);
    
    // Get preferences
    const getPrefsResponse = await axios.get(`${API_URL}/preferences/${TEST_USER_ID}`);
    console.log('✅ Get preferences response:', getPrefsResponse.data);
    
    // Test feedback endpoint
    console.log('\n🔍 Testing feedback endpoint...');
    const feedbackData = {
      userId: TEST_USER_ID,
      restaurantId: 'test-restaurant-123',
      rating: 4,
      thumbsUp: true,
      comment: 'Great food and service!'
    };
    
    const feedbackResponse = await axios.post(`${API_URL}/feedback`, feedbackData);
    console.log('✅ Feedback endpoint response:', feedbackResponse.data);
    
    // Test voice endpoint
    console.log('\n🔍 Testing voice endpoint...');
    const voiceData = {
      userId: TEST_USER_ID,
      transcription: 'I want to find a cheap Mexican restaurant near Mission District'
    };
    
    const voiceResponse = await axios.post(`${API_URL}/voice`, voiceData);
    console.log('✅ Voice endpoint response:', voiceResponse.data);
    
    // Test suggestions endpoint
    console.log('\n🔍 Testing suggestions endpoint...');
    const suggestionsData = {
      userId: TEST_USER_ID,
      location: {
        lat: 37.7749,
        lng: -122.4194
      }
    };
    
    const suggestionsResponse = await axios.post(`${API_URL}/suggestions`, suggestionsData);
    console.log('✅ Suggestions endpoint response:', suggestionsResponse.data);
    
    console.log('\n✅ All endpoints tested successfully!');
  } catch (error: any) {
    console.error('❌ Error testing endpoints:', error.response?.data || error.message);
  }
};

// Run tests
testEndpoints();
