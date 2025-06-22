/**
 * NavLife API Gateway Server
 * 
 * This server acts as a gateway between the React Native Web frontend
 * and the various backend services (weather, food, safety, transport)
 */

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const path = require('path');

// Import backend services
const { getWeatherRecommendation } = require('./agentic-weather');

// Load environment variables
dotenv.config();

const app = express();
// Use a less common port to avoid conflicts
const PORT = 9876;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// API Routes

// Weather API endpoint
app.get('/api/weather/recommendation', async (req, res) => {
  try {
    const { location } = req.query;
    
    if (!location) {
      return res.status(400).json({ 
        success: false, 
        message: 'Location parameter is required' 
      });
    }
    
    console.log(`Getting weather recommendation for ${location}...`);
    const result = await getWeatherRecommendation(location);
    res.json(result);
  } catch (error) {
    console.error('Error in weather recommendation API:', error);
    res.status(500).json({ 
      success: false, 
      message: error.message || 'Failed to get weather recommendation' 
    });
  }
});

// Food API endpoint
app.post('/api/food/search', async (req, res) => {
  try {
    const { query, location } = req.body;
    
    if (!query) {
      return res.status(400).json({ 
        success: false, 
        message: 'Query parameter is required' 
      });
    }
    
    console.log(`Searching for restaurants with query: "${query}" near ${location || 'Berkeley, CA'}...`);
    
    // This would call your food_agent_client.py
    // For now, we'll return mock data
    setTimeout(() => {
      res.json({
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
            vicinity: `123 Main St, ${location ? location.split(',')[0] : 'Berkeley'}`,
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
            vicinity: `456 Oak St, ${location ? location.split(',')[0] : 'Berkeley'}`,
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
            vicinity: `789 Pine St, ${location ? location.split(',')[0] : 'Berkeley'}`,
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
    }, 500);
  } catch (error) {
    console.error('Error in food search API:', error);
    res.status(500).json({ 
      success: false, 
      message: error.message || 'Failed to search for restaurants' 
    });
  }
});

// Safety and Transport API endpoints will be added by your friends

// Root endpoint to check if API is running
app.get('/', (req, res) => {
  res.json({ 
    status: 'NavLife API Gateway running', 
    endpoints: {
      weather: '/api/weather/recommendation?location=Berkeley',
      food: '/api/food/search (POST)'
    }
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Weather API: http://localhost:${PORT}/api/weather/recommendation?location=Berkeley`);
  console.log(`Food API: http://localhost:${PORT}/api/food/search (POST)`);
});
