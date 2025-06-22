# NavLife App

A cross-platform mobile and web application that integrates safety, transport, food discovery, and weather-based clothing recommendations.

## Features

### 1. Safety
- Safety route recommendations between locations
- Safety score calculation
- Police proximity information
- Emergency location sharing
- Live location tracking

### 2. Transport
- Multiple route options (fastest, cheapest, eco-friendly)
- Time and cost comparisons
- Integration with transit apps
- CO₂ emission information

### 3. Food Discovery
- Natural language food query processing
- Restaurant recommendations based on preferences
- Price, dietary, and cuisine filters
- Integration with Letta AI for advanced query understanding

### 4. Weather
- Current weather conditions and forecasts
- Clothing recommendations based on weather
- Detailed reasoning for recommendations
- Powered by agentic weather system with Gemini and Letta AI

## Tech Stack

- **Frontend**: React Native Web with Expo
- **UI Components**: React Native Paper
- **Navigation**: React Navigation
- **Icons**: Expo Vector Icons
- **Backend Integration**: API layer connecting to various services

## Project Structure

```
navlife-app/
├── api/                    # API integration layers
│   ├── foodApi.js          # Food discovery API integration
│   ├── safetyApi.js        # Safety features API integration
│   ├── transportApi.js     # Transport options API integration
│   └── weatherApi.js       # Weather recommendations API integration
├── screens/                # Main app screens
│   ├── FoodScreen.tsx      # Food discovery screen
│   ├── SafetyScreen.tsx    # Safety features screen
│   ├── TransportScreen.tsx # Transport options screen
│   └── WeatherScreen.tsx   # Weather recommendations screen
├── App.tsx                 # Main app component with navigation
├── package.json            # Project dependencies
└── tsconfig.json           # TypeScript configuration
```

## Backend Services

The app integrates with several backend services:

1. **Weather Service**: 
   - Located at `../agentic-weather.js`
   - Uses OpenWeatherMap API and Google Gemini for recommendations
   - Provides clothing suggestions based on weather conditions

2. **Food Discovery Service**:
   - Located at `../tools/places.ts` and `../agents/foodfinder.ts`
   - Uses Google Places API for restaurant data
   - Leverages Letta AI for natural language query understanding

3. **Safety and Transport Services**:
   - To be integrated with the frontend

## Environment Variables

The following environment variables are required:

```
OPENWEATHER_API_KEY=your_openweather_api_key
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_PLACES_API_KEY=your_google_places_api_key
LETTA_API_KEY=your_letta_api_key (optional)
```

## Running the App

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npx expo start
   ```

3. Run on web:
   ```
   npx expo start --web
   ```

4. Run on iOS simulator:
   ```
   npx expo start --ios
   ```

5. Run on Android emulator:
   ```
   npx expo start --android
   ```

## Development Notes

- The API integration layers currently use mock data for demonstration purposes
- To connect to real backend services, uncomment the fetch calls in the API files
- Backend services need to be running and accessible for full functionality
