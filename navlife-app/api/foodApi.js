/**
 * Food API integration layer
 * Connects to the food discovery backend (tools/places.ts and agents/foodfinder.ts)
 */

// Base URL for API calls - change this to your actual backend URL when deployed
const API_BASE_URL = 'http://localhost:9876';

/**
 * Search for restaurants based on natural language query and location
 * @param {string} query - Natural language query (e.g., "I want spicy Indian food")
 * @param {string} location - Location to search near (e.g., "Berkeley, CA")
 * @returns {Promise<Object>} - Restaurant search results
 */
export const searchRestaurants = async (query, location) => {
  try {
    console.log(`Searching for restaurants with query: "${query}" near ${location || 'Berkeley, CA'}...`);
    
    // Call the backend API through our server.js gateway
    try {
      const response = await fetch(`${API_BASE_URL}/api/food/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, location }),
      });
      const data = await response.json();
      return data;
    } catch (fetchError) {
      console.error('Error fetching from API:', fetchError);
      console.log('Falling back to mock data...');
      
      // Fallback to mock data if API is not available
      return new Promise((resolve) => {
        setTimeout(() => {
          // Mock response based on your food_agent_client.py and places.ts output format
          resolve({
            success: true,
            query: {
              original: query,
              parsed: {
                cuisineTypes: query.toLowerCase().includes('indian') ? ['Indian'] : 
                             query.toLowerCase().includes('mexican') ? ['Mexican'] : 
                             query.toLowerCase().includes('italian') ? ['Italian'] : ['American'],
                pricePreference: query.toLowerCase().includes('cheap') || query.toLowerCase().includes('inexpensive') ? 'low' :
                                query.toLowerCase().includes('expensive') ? 'high' : 'medium',
                dietaryRestrictions: query.toLowerCase().includes('vegan') ? ['vegan'] :
                                    query.toLowerCase().includes('vegetarian') ? ['vegetarian'] : [],
                occasion: query.toLowerCase().includes('date') ? 'date' :
                         query.toLowerCase().includes('family') ? 'family' : 'casual'
              }
            },
            restaurants: [
            {
              id: '1',
              name: query.toLowerCase().includes('indian') ? 'Curry House' : 
                   query.toLowerCase().includes('mexican') ? 'Taqueria El Sol' : 
                   query.toLowerCase().includes('italian') ? 'Pasta Paradise' : 'Local Favorite',
              rating: 4.5,
              price_level: query.toLowerCase().includes('expensive') ? 3 : 
                          query.toLowerCase().includes('cheap') ? 1 : 2,
              vicinity: `123 Main St, ${location.split(',')[0]}`,
              open_now: true,
              photos: [{
                photo_reference: 'mock-photo-reference',
                width: 400,
                height: 300
              }],
              types: query.toLowerCase().includes('indian') ? ['restaurant', 'indian'] : 
                    query.toLowerCase().includes('mexican') ? ['restaurant', 'mexican'] : 
                    query.toLowerCase().includes('italian') ? ['restaurant', 'italian'] : ['restaurant'],
              distance: 0.5,
              isOpen: true,
              categories: query.toLowerCase().includes('indian') ? ['Indian', 'Curry'] : 
                         query.toLowerCase().includes('mexican') ? ['Mexican', 'Tacos'] : 
                         query.toLowerCase().includes('italian') ? ['Italian', 'Pasta'] : ['American', 'Burgers'],
              image: 'https://via.placeholder.com/100?text=🍲',
              dietary: query.toLowerCase().includes('vegan') ? ['Vegan'] : 
                      query.toLowerCase().includes('vegetarian') ? ['Vegetarian'] : []
            },
            {
              id: '2',
              name: query.toLowerCase().includes('indian') ? 'Taste of India' : 
                   query.toLowerCase().includes('mexican') ? 'La Cantina' : 
                   query.toLowerCase().includes('italian') ? 'Bella Italia' : 'Downtown Diner',
              rating: 4.2,
              price_level: query.toLowerCase().includes('expensive') ? 3 : 
                          query.toLowerCase().includes('cheap') ? 1 : 2,
              vicinity: `456 Oak St, ${location.split(',')[0]}`,
              open_now: true,
              photos: [{
                photo_reference: 'mock-photo-reference-2',
                width: 400,
                height: 300
              }],
              types: query.toLowerCase().includes('indian') ? ['restaurant', 'indian'] : 
                    query.toLowerCase().includes('mexican') ? ['restaurant', 'mexican'] : 
                    query.toLowerCase().includes('italian') ? ['restaurant', 'italian'] : ['restaurant', 'cafe'],
              distance: 0.8,
              isOpen: true,
              categories: query.toLowerCase().includes('indian') ? ['Indian', 'Curry'] : 
                         query.toLowerCase().includes('mexican') ? ['Mexican', 'Tacos'] : 
                         query.toLowerCase().includes('italian') ? ['Italian', 'Pizza'] : ['American', 'Breakfast'],
              image: 'https://via.placeholder.com/100?text=🍽️',
              dietary: query.toLowerCase().includes('vegan') ? ['Vegan'] : 
                      query.toLowerCase().includes('vegetarian') ? ['Vegetarian'] : []
            },
            {
              id: '3',
              name: query.toLowerCase().includes('indian') ? 'Spice Garden' : 
                   query.toLowerCase().includes('mexican') ? 'Taco Town' : 
                   query.toLowerCase().includes('italian') ? 'Romano\'s' : 'The Grill House',
              rating: 3.9,
              price_level: query.toLowerCase().includes('expensive') ? 4 : 
                          query.toLowerCase().includes('cheap') ? 1 : 2,
              vicinity: `789 Pine St, ${location.split(',')[0]}`,
              open_now: false,
              photos: [{
                photo_reference: 'mock-photo-reference-3',
                width: 400,
                height: 300
              }],
              types: query.toLowerCase().includes('indian') ? ['restaurant', 'indian'] : 
                    query.toLowerCase().includes('mexican') ? ['restaurant', 'mexican'] : 
                    query.toLowerCase().includes('italian') ? ['restaurant', 'italian'] : ['restaurant', 'grill'],
              distance: 1.2,
              isOpen: false,
              categories: query.toLowerCase().includes('indian') ? ['Indian', 'Vegetarian'] : 
                         query.toLowerCase().includes('mexican') ? ['Mexican', 'Burritos'] : 
                         query.toLowerCase().includes('italian') ? ['Italian', 'Pasta'] : ['American', 'Steakhouse'],
              image: 'https://via.placeholder.com/100?text=🥘',
              dietary: query.toLowerCase().includes('vegan') ? ['Vegan'] : 
                      query.toLowerCase().includes('vegetarian') ? ['Vegetarian'] : []
            }
          ]
        });
      }, 1500);
    });
  } catch (error) {
    console.error('Error searching for restaurants:', error);
    return {
      success: false,
      message: error.message || 'Failed to search for restaurants'
    };
  }
};

/**
 * Get restaurant details by ID
 * @param {string} restaurantId - Restaurant ID
 * @returns {Promise<Object>} - Detailed restaurant information
 */
export const getRestaurantDetails = async (restaurantId) => {
  try {
    console.log(`Getting details for restaurant ID: ${restaurantId}...`);
    
    // Call the backend API through our server.js gateway
    try {
      const response = await fetch(`${API_BASE_URL}/api/food/restaurant/${restaurantId}`);
      const data = await response.json();
      return data;
    } catch (fetchError) {
      console.error('Error fetching from API:', fetchError);
      console.log('Falling back to mock data...');
      
      // Fallback to mock data if API is not available
      return new Promise((resolve) => {
        setTimeout(() => {
          // Mock response based on your places.ts output format
          resolve({
            success: true,
            restaurant: {
              id: restaurantId,
              name: restaurantId === '1' ? 'Curry House' : 
                   restaurantId === '2' ? 'Taqueria El Sol' : 'Pasta Paradise',
              rating: 4.5,
              price_level: 2,
              vicinity: '123 Main St, Berkeley',
              open_now: true,
              opening_hours: {
                weekday_text: [
                  'Monday: 11:00 AM – 10:00 PM',
                  'Tuesday: 11:00 AM – 10:00 PM',
                  'Wednesday: 11:00 AM – 10:00 PM',
                  'Thursday: 11:00 AM – 10:00 PM',
                  'Friday: 11:00 AM – 11:00 PM',
                  'Saturday: 11:00 AM – 11:00 PM',
                  'Sunday: 12:00 PM – 9:00 PM'
                ]
              },
              photos: [
                {
                  photo_reference: 'mock-photo-reference-1',
                  width: 800,
                  height: 600
                },
                {
                  photo_reference: 'mock-photo-reference-2',
                  width: 800,
                  height: 600
                }
              ],
              reviews: [
                {
                  author_name: 'John D.',
                  rating: 5,
                  text: 'Amazing food and service! Highly recommended.',
                  time: new Date().getTime() - 86400000 // 1 day ago
                },
                {
                  author_name: 'Sarah M.',
                  rating: 4,
                  text: 'Great food, but a bit crowded during peak hours.',
                  time: new Date().getTime() - 172800000 // 2 days ago
                }
              ],
              types: restaurantId === '1' ? ['restaurant', 'indian'] : 
                    restaurantId === '2' ? ['restaurant', 'mexican'] : ['restaurant', 'italian'],
              website: 'https://example.com/restaurant',
              phone_number: '+1 (555) 123-4567',
              distance: 0.5,
              isOpen: true,
              categories: restaurantId === '1' ? ['Indian', 'Curry'] : 
                         restaurantId === '2' ? ['Mexican', 'Tacos'] : ['Italian', 'Pasta'],
              image: 'https://via.placeholder.com/400x300?text=Restaurant',
              dietary: ['Vegetarian options available']
            }
          });
        }, 800);
      });
    }
  } catch (error) {
    console.error('Error getting restaurant details:', error);
    return {
      success: false,
      message: error.message || 'Failed to get restaurant details'
    };
  }
};
