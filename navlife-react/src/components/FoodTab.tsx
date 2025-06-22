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
  Rating,
  Link,
} from '@mui/material';
import {
  Restaurant as FoodIcon,
  Phone as PhoneIcon,
  Language as WebsiteIcon,
  LocationOn as LocationIcon,
  AccessTime as TimeIcon,
} from '@mui/icons-material';
import { apiService, FoodSearchResult, Restaurant } from '../services/api';

const FoodTab: React.FC = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('Berkeley, CA');
  const [foodData, setFoodData] = useState<FoodSearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearchRestaurants = async () => {
    if (!query.trim()) {
      setError('Please enter what you are craving');
      return;
    }

    setLoading(true);
    setError(null);
    setFoodData(null);

    try {
      const data = await apiService.searchRestaurants(query, location);
      setFoodData(data);
      if (!data.success) {
        setError(data.message || 'Failed to search restaurants');
      }
    } catch (err) {
      setError('An error occurred while searching restaurants');
      console.error('Food API error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderPriceLevel = (priceLevel: number) => {
    return '$'.repeat(priceLevel) || 'N/A';
  };

  const renderRestaurantCard = (restaurant: Restaurant, index: number) => {
    const fullStars = Math.floor(restaurant.rating);
    const hasHalfStar = restaurant.rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <Card key={index} sx={{ mb: 2, height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              {restaurant.name}
            </Typography>
            <Chip
              label={restaurant.isOpen ? 'Open' : 'Closed'}
              color={restaurant.isOpen ? 'success' : 'error'}
              size="small"
              icon={<TimeIcon />}
            />
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Rating value={restaurant.rating} precision={0.5} readOnly size="small" />
            <Typography variant="body2" sx={{ ml: 1 }}>
              {restaurant.rating} ({fullStars}★{hasHalfStar ? '½' : ''}{'☆'.repeat(emptyStars)})
            </Typography>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            <strong>Price:</strong> {renderPriceLevel(restaurant.price_level)}
          </Typography>

          <Typography variant="body2" sx={{ mb: 2 }}>
            <LocationIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
            {restaurant.address}
          </Typography>

          {restaurant.phone && (
            <Typography variant="body2" sx={{ mb: 1 }}>
              <PhoneIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
              {restaurant.phone}
            </Typography>
          )}

          {restaurant.website && (
            <Typography variant="body2" sx={{ mb: 2 }}>
              <WebsiteIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
              <Link href={restaurant.website} target="_blank" rel="noopener">
                Visit Website
              </Link>
            </Typography>
          )}

          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {restaurant.types.map((type, typeIndex) => (
              <Chip
                key={typeIndex}
                label={type}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.75rem' }}
              />
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <FoodIcon color="primary" />
        Restaurant Discovery
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="What are you craving?"
                placeholder="e.g., spicy Indian food with outdoor seating"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearchRestaurants()}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Location"
                placeholder="e.g., Berkeley, CA"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearchRestaurants()}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleSearchRestaurants}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <FoodIcon />}
                sx={{ height: 56 }}
              >
                {loading ? 'Searching...' : 'Search'}
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

      {foodData && foodData.success && (
        <Box>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Search Results
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Query:</strong> "{foodData.original_query}"
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>Parsed as:</strong> {JSON.stringify(foodData.query_analysis, null, 2)}
            </Typography>
            <Typography variant="h6" sx={{ mt: 2 }}>
              Restaurants ({foodData.restaurants.length})
            </Typography>
          </Paper>

          <Grid container spacing={2}>
            {foodData.restaurants.map((restaurant, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                {renderRestaurantCard(restaurant, index)}
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default FoodTab; 