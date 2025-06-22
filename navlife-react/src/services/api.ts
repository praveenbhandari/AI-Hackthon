import axios from 'axios';

// API Base URLs - All services on port 8000 (FastAPI backend)
const API_BASE_URL = "http://localhost:8000";  // BC CrewAI FastAPI backend

// Create axios instance with default config
const api = axios.create({
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface WeatherData {
  success: boolean;
  weather?: {
    city: string;
    country: string;
    temperature: number;
    feels_like: number;
    description: string;
    humidity: number;
    wind_speed: number;
  };
  recommendation?: {
    top: string;
    bottom: string;
    outerwear: string;
    footwear: string;
    accessories: string[];
  };
  reasoning?: string;
  message?: string;
}

export interface Restaurant {
  name: string;
  rating: number;
  price_level: number;
  isOpen: boolean;
  address: string;
  phone: string;
  website: string;
  types: string[];
  photos: string[];
}

export interface FoodSearchResult {
  success: boolean;
  original_query: string;
  processed_query: string;
  query_analysis: any;
  restaurants: Restaurant[];
  message?: string;
}

export interface TransportRoute {
  success: boolean;
  routes: any[];
  data?: {
    transit_routes: any[];
  };
  message?: string;
}

export interface ResearchResult {
  success: boolean;
  research: any;
  message?: string;
}

export interface SafetyRoute {
  success: boolean;
  route: any;
  safety_score: number;
  distance: number;
  duration: number;
  message?: string;
}

export interface BCHealthCheck {
  status: string;
  message: string;
}

export interface BCAgentsInfo {
  success: boolean;
  agents: any[];
  message?: string;
}

export interface BCTasksInfo {
  success: boolean;
  tasks: any[];
  message?: string;
}

// API Functions
export const apiService = {
  // Weather API - Mock for now since not in FastAPI
  async getWeatherRecommendation(location: string): Promise<WeatherData> {
    try {
      // Mock response since weather endpoint not in FastAPI
      return {
        success: true,
        weather: {
          city: location,
          country: "US",
          temperature: 22,
          feels_like: 24,
          description: "Partly cloudy",
          humidity: 65,
          wind_speed: 5
        },
        recommendation: {
          top: "Light sweater or long-sleeve shirt",
          bottom: "Jeans or comfortable pants",
          outerwear: "Light jacket",
          footwear: "Comfortable walking shoes",
          accessories: ["Sunglasses", "Hat"]
        },
        reasoning: "Temperature is moderate with light wind. Comfortable clothing recommended."
      };
    } catch (error) {
      console.error('Weather API error:', error);
      return {
        success: false,
        message: 'Failed to get weather recommendations'
      };
    }
  },

  // Food API - Mock for now since not in FastAPI
  async searchRestaurants(query: string, location: string = "Berkeley, CA"): Promise<FoodSearchResult> {
    try {
      // Mock response since food endpoint not in FastAPI
      return {
        success: true,
        original_query: query,
        processed_query: query,
        query_analysis: { cuisine: "various", price_range: "moderate" },
        restaurants: [
          {
            name: "Sample Restaurant",
            rating: 4.5,
            price_level: 2,
            isOpen: true,
            address: "123 Main St, Berkeley, CA",
            phone: "(555) 123-4567",
            website: "https://example.com",
            types: ["restaurant", "food"],
            photos: []
          }
        ]
      };
    } catch (error) {
      console.error('Food API error:', error);
      return {
        success: false,
        original_query: query,
        processed_query: query,
        query_analysis: {},
        restaurants: [],
        message: 'Failed to search restaurants'
      };
    }
  },

  // Transport API - Call transit planner agent
  async getTransportRoutes(userRequest: string, origin: string, destination: string, time: string): Promise<TransportRoute> {
    try {
      const response = await api.post(`${API_BASE_URL}/agents/transit_planner_json`, {
        user_request: userRequest,
        origin: origin,
        destination: destination,
        time: time,
        topic: "Transit Planning"
      });
      return response.data;
    } catch (error) {
      console.error('Transport API error:', error);
      return {
        success: false,
        routes: [],
        message: 'Failed to get transport routes'
      };
    }
  },

  // Research API - Call researcher agent
  async getResearch(topic: string, currentYear: string): Promise<ResearchResult> {
    try {
      const response = await api.post(`${API_BASE_URL}/agents/researcher`, {
        topic: topic,
        current_year: currentYear
      });
      return response.data;
    } catch (error) {
      console.error('Research API error:', error);
      return {
        success: false,
        research: null,
        message: 'Failed to get research results'
      };
    }
  },

  // Full Crew API - Call multiple agents
  async getFullCrew(userRequest: string, topic: string, origin?: string, destination?: string, time?: string): Promise<any> {
    try {
      // Call multiple agents for full crew analysis
      const [researcher, transitPlanner, routeOptimizer] = await Promise.all([
        api.post(`${API_BASE_URL}/agents/researcher`, {
          topic: topic,
          current_year: new Date().getFullYear().toString()
        }),
        api.post(`${API_BASE_URL}/agents/transit_planner`, {
          user_request: userRequest,
          origin: origin,
          destination: destination,
          time: time,
          topic: "Transit Planning"
        }),
        api.post(`${API_BASE_URL}/agents/route_optimizer`, {
          user_request: userRequest,
          origin: origin,
          destination: destination,
          topic: "Route Optimization"
        })
      ]);

      return {
        success: true,
        result: {
          user_request: userRequest,
          topic: topic,
          origin: origin,
          destination: destination,
          time: time,
          research: researcher.data,
          transit_planning: transitPlanner.data,
          route_optimization: routeOptimizer.data
        }
      };
    } catch (error) {
      console.error('Full Crew API error:', error);
      return {
        success: false,
        message: 'Failed to execute full crew request'
      };
    }
  },

  // Safety Route API - Call safety router agent
  async getSafetyRoute(startLat: number, startLng: number, endLat: number, endLng: number, safetyWeight: number = 0.7): Promise<SafetyRoute> {
    try {
      const userRequest = `Find safe route from ${startLat},${startLng} to ${endLat},${endLng}`;
      const response = await api.post(`${API_BASE_URL}/agents/safety_router`, {
        user_request: userRequest,
        origin: safetyWeight.toString(),
        topic: "Safety Routing"
      });
      return response.data;
    } catch (error) {
      console.error('Safety Route API error:', error);
      return {
        success: false,
        route: null,
        safety_score: 0,
        distance: 0,
        duration: 0,
        message: 'Failed to get safety route'
      };
    }
  },

  // Enhanced Safety Route API - Call advanced safety router
  async getEnhancedSafetyRoute(
    startLat: number, 
    startLng: number, 
    endLat: number, 
    endLng: number, 
    safetyWeight: number = 0.7, 
    maxDistanceFactor: number = 2.0
  ): Promise<any> {
    try {
      const userRequest = `Find safe route from ${startLat},${startLng} to ${endLat},${endLng}`;
      const response = await api.post(`${API_BASE_URL}/agents/safety_router_advanced`, {
        user_request: userRequest,
        origin: safetyWeight.toString(),
        topic: "Advanced Safety Routing"
      });
      return response.data;
    } catch (error) {
      console.error('Enhanced Safety Route API error:', error);
      return {
        success: false,
        message: 'Failed to get enhanced safety route'
      };
    }
  },

  // Safety Info API - Call safety info endpoint
  async getSafetyInfo(lat: number, lng: number): Promise<any> {
    try {
      const response = await api.post(`${API_BASE_URL}/safety/info`, {
        lat: lat,
        lng: lng
      });
      return response.data;
    } catch (error) {
      console.error('Safety Info API error:', error);
      return {
        success: false,
        message: 'Failed to get safety information'
      };
    }
  },

  // Health Check API - Call health endpoint
  async checkBCHealth(): Promise<BCHealthCheck> {
    try {
      const response = await api.get(`${API_BASE_URL}/health`);
      return response.data;
    } catch (error) {
      console.error('Health Check API error:', error);
      return {
        status: 'error',
        message: 'Backend service unavailable'
      };
    }
  },

  // BC Agents Info - Call agents info endpoint
  async getBCAgentsInfo(): Promise<BCAgentsInfo> {
    try {
      const response = await api.get(`${API_BASE_URL}/agents/info`);
      return response.data;
    } catch (error) {
      console.error('BC Agents Info API error:', error);
      return {
        success: false,
        agents: [],
        message: 'Failed to get agents information'
      };
    }
  },

  // BC Tasks Info - Call status endpoint
  async getBCTasksInfo(): Promise<BCTasksInfo> {
    try {
      const response = await api.get(`${API_BASE_URL}/status`);
      return response.data;
    } catch (error) {
      console.error('BC Tasks Info API error:', error);
      return {
        success: false,
        tasks: [],
        message: 'Failed to get tasks information'
      };
    }
  }
};

export default apiService; 