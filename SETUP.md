# NavLife Application Setup Guide

This guide will help you set up and run the NavLife application, including both the frontend React Native Web app and the backend API gateway.

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- API keys for:
  - OpenWeatherMap
  - Google Gemini
  - Google Places
  - Letta AI (optional)

## Environment Setup

1. Clone the repository (if you haven't already):
   ```
   git clone <repository-url>
   cd AI-Hackthon
   ```

2. Create a `.env` file in the root directory based on the `.env.example` file:
   ```
   cp .env.example .env
   ```

3. Add your API keys to the `.env` file:
   ```
   GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
   LETTA_API_KEY=your_letta_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Backend Setup

1. Install dependencies for the backend:
   ```
   npm install
   ```

2. Start the API gateway server:
   ```
   npm start
   ```
   
   This will start the server on http://localhost:3000

## Frontend Setup

1. Navigate to the navlife-app directory:
   ```
   cd navlife-app
   ```

2. Install dependencies for the frontend:
   ```
   npm install
   ```

3. Start the Expo development server:
   ```
   npx expo start
   ```

4. Choose your platform:
   - For web: Press `w` or click on "Run in web browser"
   - For iOS: Press `i` (requires macOS and Xcode)
   - For Android: Press `a` (requires Android Studio)

## Application Structure

### Backend Components

- `server.js`: API gateway that connects the frontend to backend services
- `agentic-weather.js`: Weather recommendation service using OpenWeatherMap and Gemini
- `agents/foodfinder.ts`: Food discovery agent with Letta integration
- `agents/weatheragent.ts`: Weather agent with Letta integration
- `tools/places.ts`: Google Places API integration for restaurant search

### Frontend Components

- `navlife-app/App.tsx`: Main application with tab navigation
- `navlife-app/screens/`: UI screens for each feature
  - `SafetyScreen.tsx`: Safety features UI
  - `TransportScreen.tsx`: Transport options UI
  - `FoodScreen.tsx`: Food discovery UI
  - `WeatherScreen.tsx`: Weather recommendations UI
- `navlife-app/api/`: API integration layers
  - `weatherApi.js`: Weather API integration
  - `foodApi.js`: Food API integration

## Testing the Application

1. Weather Feature:
   - Open the Weather tab
   - Enter a location (e.g., "Berkeley, CA")
   - View weather conditions and clothing recommendations

2. Food Feature:
   - Open the Food tab
   - Enter a food query (e.g., "I want spicy Indian food")
   - View restaurant recommendations

3. Transport Feature:
   - Open the Transport tab
   - Enter start and end locations
   - View transport options

4. Safety Feature:
   - Open the Safety tab
   - View safety features (implementation in progress)

## Troubleshooting

- If you encounter CORS issues, make sure the API gateway server is running
- If API calls fail, check that your API keys are correctly set in the `.env` file
- For TypeScript errors, ensure you have the correct types installed

## Development Notes

- The API integration layers currently use mock data as fallbacks when API calls fail
- To connect to real backend services, ensure the server.js API gateway is running
- Backend services need to be properly configured with API keys for full functionality
