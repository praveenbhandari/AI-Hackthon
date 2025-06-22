import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  Paper,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import { WbSunny as WeatherIcon, CheckCircle as SuccessIcon } from '@mui/icons-material';
import { apiService, WeatherData } from '../services/api';

const WeatherTab: React.FC = () => {
  const [location, setLocation] = useState('Berkeley,CA,US');
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGetRecommendations = async () => {
    if (!location.trim()) {
      setError('Please enter a location');
      return;
    }

    setLoading(true);
    setError(null);
    setWeatherData(null);

    try {
      const data = await apiService.getWeatherRecommendation(location);
      setWeatherData(data);
      if (!data.success) {
        setError(data.message || 'Failed to get weather recommendations');
      }
    } catch (err) {
      setError('An error occurred while fetching weather data');
      console.error('Weather API error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderWeatherInfo = (weather: WeatherData['weather']) => {
    if (!weather) return null;

    return (
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WeatherIcon color="primary" />
          Current Weather in {weather.city}, {weather.country}
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="h4" color="primary" gutterBottom>
              {weather.temperature}°C
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Feels like {weather.feels_like}°C
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1" gutterBottom>
              <strong>Conditions:</strong> {weather.description}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Humidity:</strong> {weather.humidity}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Wind Speed:</strong> {weather.wind_speed} m/s
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    );
  };

  const renderRecommendations = (recommendation: WeatherData['recommendation']) => {
    if (!recommendation) return null;

    return (
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SuccessIcon color="success" />
          Clothing Recommendations
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1" gutterBottom>
              <strong>Top:</strong> {recommendation.top}
            </Typography>
            <Typography variant="body1" gutterBottom>
              <strong>Bottom:</strong> {recommendation.bottom}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1" gutterBottom>
              <strong>Outerwear:</strong> {recommendation.outerwear}
            </Typography>
            <Typography variant="body1" gutterBottom>
              <strong>Footwear:</strong> {recommendation.footwear}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body1" gutterBottom>
              <strong>Accessories:</strong>
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {recommendation.accessories.map((accessory, index) => (
                <Chip key={index} label={accessory} size="small" variant="outlined" />
              ))}
            </Box>
          </Grid>
        </Grid>
      </Paper>
    );
  };

  const renderReasoning = (reasoning: string | undefined) => {
    if (!reasoning) return null;

    return (
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Reasoning
        </Typography>
        <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
          {reasoning}
        </Typography>
      </Paper>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <WeatherIcon color="primary" />
        Weather-Based Clothing Recommendations
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={8}>
              <TextField
                fullWidth
                label="Location"
                placeholder="Enter location (e.g., Berkeley,CA,US)"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleGetRecommendations()}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleGetRecommendations}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <WeatherIcon />}
                sx={{ height: 56 }}
              >
                {loading ? 'Getting Recommendations...' : 'Get Recommendations'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {weatherData && weatherData.success && (
        <Box>
          {renderWeatherInfo(weatherData.weather)}
          {renderRecommendations(weatherData.recommendation)}
          {renderReasoning(weatherData.reasoning)}
        </Box>
      )}
    </Box>
  );
};

export default WeatherTab; 