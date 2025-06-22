# NavLife React App

A modern React frontend for the NavLife application, converted from the original Gradio interface. This application provides weather-based clothing recommendations, restaurant discovery, transit planning, research capabilities, and enhanced safety routing.

## Features

### 🌤️ Weather Tab
- Get weather-based clothing recommendations for any location
- Displays current weather conditions (temperature, humidity, wind speed)
- Provides detailed clothing suggestions with reasoning

### 🍽️ Food Tab
- Search for restaurants using natural language queries
- Displays restaurant details including ratings, prices, and contact information
- Shows restaurant types and current open/closed status

### 🚌 Transport Tab
- BC CrewAI transit route planning
- Find optimal routes between locations
- Detailed route information with steps and alternatives

### 🔬 Research Tab
- BC CrewAI research capabilities
- Conduct research on various topics
- Get summaries, key findings, and recommendations

### 🚀 Full Crew Tab
- Combined research and transit planning
- Integrated analysis of research and route data
- Comprehensive recommendations

### 📊 BC Info Tab
- View BC CrewAI agents and their capabilities
- Check available tasks and their details
- Monitor system status

### 🛡️ Safety Tab
- Enhanced safety route finding with interactive maps
- Safety information for specific locations
- Configurable safety weights and distance factors

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Material-UI (MUI)** for modern UI components
- **React Router** for navigation
- **Axios** for API communication
- **Leaflet** for map visualization

### Backend
- **Flask** API server
- **Flask-CORS** for cross-origin requests
- **Requests** for external API communication

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- Access to the original NavLife backend services

## Installation

### 1. Clone and Setup React Frontend

```bash
cd navlife-react
npm install
```

### 2. Setup Backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Setup

Make sure the following services are running:
- BC CrewAI API (port 8000)
- Safety Router API (port 8001)
- Weather and Food agent services

## Running the Application

### 1. Start the Backend API Server

```bash
cd backend
python app.py
```

The Flask backend will start on `http://localhost:5000`

### 2. Start the React Development Server

```bash
npm start
```

The React app will start on `http://localhost:3000`

## Project Structure

```
navlife-react/
├── src/
│   ├── components/          # React components
│   │   ├── Navbar.tsx      # Navigation bar
│   │   ├── WeatherTab.tsx  # Weather recommendations
│   │   ├── FoodTab.tsx     # Restaurant discovery
│   │   ├── TransportTab.tsx # Transit planning
│   │   ├── ResearchTab.tsx # Research functionality
│   │   ├── FullCrewTab.tsx # Full crew operations
│   │   ├── BCInfoTab.tsx   # BC CrewAI information
│   │   └── SafetyTab.tsx   # Safety routing
│   ├── services/
│   │   └── api.ts          # API service layer
│   ├── App.tsx             # Main app component
│   └── index.tsx           # App entry point
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── public/                 # Static assets
└── package.json           # Node.js dependencies
```

## API Endpoints

The Flask backend provides the following endpoints:

- `POST /weather` - Weather recommendations
- `POST /food` - Restaurant search
- `POST /transit` - Transport routes
- `POST /research` - Research functionality
- `POST /full-crew` - Full crew operations
- `POST /safety/route` - Safety routes
- `POST /safety/enhanced-route` - Enhanced safety routes
- `POST /safety/safety-info` - Safety information
- `GET /bc/health` - BC CrewAI health check
- `GET /bc/agents` - BC CrewAI agents info
- `GET /bc/tasks` - BC CrewAI tasks info

## Key Features

### Modern UI/UX
- Responsive design that works on desktop and mobile
- Material-UI components for consistent styling
- Intuitive navigation with tab-based interface
- Loading states and error handling

### Real-time Data
- Live weather data and recommendations
- Real-time restaurant search results
- Dynamic route planning with safety considerations

### Interactive Maps
- Safety route visualization
- Location-based safety information
- Interactive map components

### Error Handling
- Comprehensive error handling throughout the application
- User-friendly error messages
- Graceful degradation when services are unavailable

## Development

### Adding New Features

1. Create new components in `src/components/`
2. Add API endpoints in `backend/app.py`
3. Update the API service in `src/services/api.ts`
4. Add routing in `src/App.tsx`

### Styling

The application uses Material-UI theming. Customize the theme in `src/App.tsx`:

```typescript
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    // ... other theme options
  },
});
```

### API Integration

All API calls are centralized in `src/services/api.ts`. Add new API functions here:

```typescript
export const apiService = {
  // ... existing functions
  async newFunction(): Promise<any> {
    // Implementation
  }
};
```

## Deployment

### Build for Production

```bash
npm run build
```

### Deploy Backend

The Flask backend can be deployed using:
- Heroku
- AWS
- Google Cloud Platform
- Any Python hosting service

### Environment Variables

Set the following environment variables for production:

```bash
REACT_APP_API_BASE_URL=https://your-backend-url.com
REACT_APP_SAFETY_API_URL=https://your-safety-api-url.com
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the Flask backend has CORS properly configured
2. **API Connection Issues**: Check that all backend services are running
3. **Map Loading Issues**: Verify Leaflet CSS is properly imported

### Debug Mode

Enable debug mode in the Flask backend:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the NavLife application suite.

## Support

For issues and questions, please refer to the main NavLife project documentation.
