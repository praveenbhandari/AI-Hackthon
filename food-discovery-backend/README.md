# Food Discovery Backend

A backend-only module for a "Food Discovery" feature inside a holistic app for international students visiting San Francisco. This module suggests food places by cuisine, price, and open/close hours using natural language input and an AI agent to reason over the request.

## Features

- **Natural Language Processing**: Accept natural language queries like "Find a cheap halal place open near Mission District"
- **User Preferences**: Store and retrieve user preferences for personalized recommendations
- **Feedback System**: Accept thumbs up/down or text feedback on recommendations
- **Voice Input**: Process transcribed speech input for food recommendations
- **Proactive Suggestions**: Generate food suggestions based on time, location, and user preferences

## Tech Stack

- **Language**: TypeScript
- **Framework**: Express.js
- **Database**: Supabase (PostgreSQL)
- **Agent Reasoning**: Custom implementation inspired by Mastra
- **LLM**: Google Gemini API (for natural language parsing)
- **External APIs**:
  - Google Places API (primary data source)
  - Yelp Fusion API (fallback for pricing, ratings, or extra info)

## Project Structure

```
food-discovery-backend/
├── src/
│   ├── agents/         # AI agent logic for reasoning
│   ├── config/         # Configuration for external services
│   ├── controllers/    # HTTP request handlers
│   ├── routes/         # API route definitions
│   ├── services/       # Business logic
│   ├── types/          # TypeScript interfaces
│   ├── utils/          # Helper functions
│   └── index.ts        # Application entry point
├── .env                # Environment variables (not committed)
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore file
├── package.json        # Project dependencies
├── tsconfig.json       # TypeScript configuration
└── README.md           # Project documentation
```

## API Endpoints

### 1. Query Endpoint

```
POST /query
```

Process natural language food queries.

**Request Body**:
```json
{
  "query": "Find a cheap halal place open near Mission District",
  "userId": "user123" // Optional
}
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "place123",
      "name": "Halal Food Corner",
      "address": "123 Mission St, San Francisco, CA",
      "priceLevel": 1,
      "isOpen": true,
      "rating": 4.5,
      "photos": ["https://example.com/photo1.jpg"]
    }
  ],
  "message": "Found 1 restaurants matching your query"
}
```

### 2. Preferences Endpoint

```
GET /preferences/:userId
```

Retrieve user preferences.

**Response**:
```json
{
  "success": true,
  "data": {
    "userId": "user123",
    "dietaryRestrictions": ["vegetarian"],
    "cuisinePreferences": ["italian", "indian"],
    "priceRange": 2,
    "spicyLevel": 3,
    "favoriteRestaurants": ["place123", "place456"],
    "avoidRestaurants": ["place789"],
    "createdAt": "2025-06-21T14:00:00.000Z",
    "updatedAt": "2025-06-21T14:00:00.000Z"
  },
  "message": "User preferences retrieved successfully"
}
```

```
POST /preferences
```

Save user preferences.

**Request Body**:
```json
{
  "userId": "user123",
  "dietaryRestrictions": ["vegetarian"],
  "cuisinePreferences": ["italian", "indian"],
  "priceRange": 2,
  "spicyLevel": 3
}
```

### 3. Feedback Endpoint

```
POST /feedback
```

Accept user feedback on recommendations.

**Request Body**:
```json
{
  "userId": "user123",
  "restaurantId": "place123",
  "rating": 4,
  "thumbsUp": true,
  "comment": "Great food and service!"
}
```

### 4. Voice Endpoint

```
POST /voice
```

Process transcribed speech input.

**Request Body**:
```json
{
  "userId": "user123",
  "transcription": "I want to find a cheap Italian restaurant near Union Square"
}
```

### 5. Suggestions Endpoint

```
POST /suggestions
```

Generate proactive food suggestions.

**Request Body**:
```json
{
  "userId": "user123",
  "location": {
    "lat": 37.7749,
    "lng": -122.4194
  },
  "time": "2025-06-21T18:30:00.000Z"
}
```

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Copy `.env.example` to `.env` and fill in your API keys:
   ```
   cp .env.example .env
   ```
4. Set up a Supabase project and create the following tables:
   - `preferences`: Store user preferences
   - `feedback`: Store user feedback

5. Start the development server:
   ```
   npm run dev
   ```

## Testing the API

You can test the API using Postman or curl commands:

```bash
# Example curl command to test the query endpoint
curl -X POST http://localhost:3000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find a cheap halal place open near Mission District"}'
```

## Environment Variables

The following environment variables are required:

```
# API Keys
GOOGLE_PLACES_API_KEY=your_google_places_api_key
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
YELP_API_KEY=your_yelp_api_key

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Server Configuration
PORT=3000
NODE_ENV=development
```
