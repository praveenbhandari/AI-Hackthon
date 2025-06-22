import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Image, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from 'react-native-paper';
import { getWeatherRecommendation } from '../api/weatherApi';

// Define interfaces for weather data
interface ForecastDay {
  date: string;
  temperature: {
    min: number;
    max: number;
  };
  description: string;
  icon: string;
  precipitation_probability: number;
}

interface WeatherData {
  city: string;
  country: string;
  temperature: number;
  feels_like: number;
  description: string;
  humidity: number;
  wind_speed: number;
  icon: string;
  forecast: ForecastDay[];
  timeOfDay: 'day' | 'night';
}

interface ClothingRecommendation {
  top: string;
  bottom: string;
  outerwear: string;
  accessories: string[];
  footwear: string;
  additional_tips: string[];
}

interface WeatherResponse {
  success: boolean;
  weather: WeatherData;
  recommendation: ClothingRecommendation;
  reasoning: string;
  source: string;
  message?: string;
}

// This would be replaced with actual API calls to your agentic-weather.js backend
const mockWeatherData: WeatherResponse = {
  success: true,
  weather: {
    city: "Berkeley",
    country: "US",
    temperature: 14.45,
    feels_like: 13.86,
    description: "clear sky",
    humidity: 73,
    wind_speed: 0.89,
    icon: "01n",
    forecast: [
      {
        date: "2025-06-22",
        temperature: {
          min: 12.31,
          max: 24.11
        },
        description: "clear sky",
        icon: "01n",
        precipitation_probability: 0
      },
      {
        date: "2025-06-23",
        temperature: {
          min: 12.37,
          max: 22.41
        },
        description: "clear sky",
        icon: "01d",
        precipitation_probability: 0
      },
      {
        date: "2025-06-24",
        temperature: {
          min: 12.46,
          max: 16.86
        },
        description: "clear sky",
        icon: "01d",
        precipitation_probability: 0
      }
    ],
    timeOfDay: "night"
  },
  recommendation: {
    top: "Long-sleeved t-shirt or light sweater",
    bottom: "Jeans or chinos",
    outerwear: "Light jacket or hoodie",
    accessories: [
      "Light scarf (optional)",
      "Watch"
    ],
    footwear: "Sneakers or comfortable walking shoes",
    additional_tips: [
      "Dress in layers as temperatures will increase throughout the day.",
      "Consider a hat for sun protection during the day."
    ]
  },
  reasoning: "It's currently night in Berkeley with a temperature of 14.45°C, which feels like 13.86°C. A long-sleeved t-shirt or light sweater will provide enough warmth for the cool night air. Jeans or chinos are suitable for the bottom. A light jacket or hoodie is recommended as an outer layer for extra warmth during the night and cooler morning hours.",
  source: "gemini"
};

const WeatherScreen = () => {
  const [location, setLocation] = useState('Berkeley');
  const [weatherData, setWeatherData] = useState(mockWeatherData);
  const [loading, setLoading] = useState(false);

  // Connect to the agentic-weather.js backend via the weatherApi integration
  const fetchWeatherRecommendation = async (searchLocation) => {
    if (!searchLocation.trim()) return;
    
    setLoading(true);
    
    try {
      const result = await getWeatherRecommendation(searchLocation);
      
      if (result.success) {
        setWeatherData(result);
      } else {
        console.error('Error from weather API:', result.message);
        setWeatherData({
          success: false,
          message: result.message || 'Failed to get weather recommendation'
        });
      }
    } catch (error) {
      console.error('Error fetching weather data:', error);
      setWeatherData({
        success: false,
        message: error.message || 'An error occurred while getting weather data'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeatherRecommendation(location);
  }, []);

  const handleSearch = () => {
    fetchWeatherRecommendation(location);
  };

  const getWeatherIcon = (iconCode, timeOfDay) => {
    const iconMap = {
      '01d': 'sunny',
      '01n': 'moon',
      '02d': 'partly-sunny',
      '02n': 'cloudy-night',
      '03d': 'cloud',
      '03n': 'cloud',
      '04d': 'cloudy',
      '04n': 'cloudy',
      '09d': 'rainy',
      '09n': 'rainy',
      '10d': 'rainy',
      '10n': 'rainy',
      '11d': 'thunderstorm',
      '11n': 'thunderstorm',
      '13d': 'snow',
      '13n': 'snow',
      '50d': 'water',
      '50n': 'water'
    };
    
    return iconMap[iconCode] || 'cloud';
  };

  return (
    <View style={styles.container}>
      {/* Search Section */}
      <View style={styles.searchContainer}>
        <Text style={styles.searchLabel}>Check weather and clothing recommendations</Text>
        <View style={styles.searchInputContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Enter city name (e.g., Berkeley)"
            value={location}
            onChangeText={setLocation}
          />
          <TouchableOpacity 
            style={styles.searchButton} 
            onPress={handleSearch}
            disabled={loading}
          >
            <Ionicons name={loading ? "refresh" : "search"} size={20} color="#fff" />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView style={styles.contentContainer}>
        {weatherData && weatherData.success ? (
          <>
            {/* Current Weather Card */}
            <Card style={styles.weatherCard}>
              <View style={styles.weatherHeader}>
                <View style={styles.weatherLocation}>
                  <Text style={styles.cityName}>{weatherData.weather.city}</Text>
                  <Text style={styles.countryName}>{weatherData.weather.country}</Text>
                </View>
                <Ionicons 
                  name={getWeatherIcon(weatherData.weather.icon, weatherData.weather.timeOfDay)} 
                  size={48} 
                  color="#4169e1" 
                />
              </View>
              
              <View style={styles.weatherDetails}>
                <View style={styles.temperatureContainer}>
                  <Text style={styles.temperature}>{weatherData.weather.temperature.toFixed(1)}°C</Text>
                  <Text style={styles.feelsLike}>Feels like {weatherData.weather.feels_like.toFixed(1)}°C</Text>
                </View>
                
                <View style={styles.conditionsContainer}>
                  <Text style={styles.weatherDescription}>{weatherData.weather.description}</Text>
                  <View style={styles.weatherMetrics}>
                    <View style={styles.metric}>
                      <Ionicons name="water" size={16} color="#4169e1" />
                      <Text style={styles.metricText}>{weatherData.weather.humidity}%</Text>
                    </View>
                    <View style={styles.metric}>
                      <Ionicons name="speedometer" size={16} color="#4169e1" />
                      <Text style={styles.metricText}>{weatherData.weather.wind_speed} m/s</Text>
                    </View>
                  </View>
                </View>
              </View>
            </Card>

            {/* Clothing Recommendations Card */}
            <Card style={styles.recommendationCard}>
              <Text style={styles.recommendationTitle}>Clothing Recommendations</Text>
              
              <View style={styles.recommendationItem}>
                <Ionicons name="shirt" size={24} color="#4169e1" />
                <View style={styles.recommendationContent}>
                  <Text style={styles.recommendationLabel}>Top</Text>
                  <Text style={styles.recommendationText}>{weatherData.recommendation.top}</Text>
                </View>
              </View>
              
              <View style={styles.recommendationItem}>
                <Ionicons name="cut" size={24} color="#4169e1" />
                <View style={styles.recommendationContent}>
                  <Text style={styles.recommendationLabel}>Bottom</Text>
                  <Text style={styles.recommendationText}>{weatherData.recommendation.bottom}</Text>
                </View>
              </View>
              
              <View style={styles.recommendationItem}>
                <Ionicons name="jacket" size={24} color="#4169e1" />
                <View style={styles.recommendationContent}>
                  <Text style={styles.recommendationLabel}>Outerwear</Text>
                  <Text style={styles.recommendationText}>{weatherData.recommendation.outerwear}</Text>
                </View>
              </View>
              
              <View style={styles.recommendationItem}>
                <Ionicons name="watch" size={24} color="#4169e1" />
                <View style={styles.recommendationContent}>
                  <Text style={styles.recommendationLabel}>Accessories</Text>
                  <Text style={styles.recommendationText}>
                    {weatherData.recommendation.accessories.join(', ')}
                  </Text>
                </View>
              </View>
              
              <View style={styles.recommendationItem}>
                <Ionicons name="footsteps" size={24} color="#4169e1" />
                <View style={styles.recommendationContent}>
                  <Text style={styles.recommendationLabel}>Footwear</Text>
                  <Text style={styles.recommendationText}>{weatherData.recommendation.footwear}</Text>
                </View>
              </View>
            </Card>

            {/* Additional Tips Card */}
            <Card style={styles.tipsCard}>
              <Text style={styles.tipsTitle}>Additional Tips</Text>
              {weatherData.recommendation.additional_tips.map((tip, index) => (
                <View key={index} style={styles.tipItem}>
                  <Ionicons name="bulb" size={20} color="#ffc107" />
                  <Text style={styles.tipText}>{tip}</Text>
                </View>
              ))}
            </Card>

            {/* Reasoning Card */}
            <Card style={styles.reasoningCard}>
              <Text style={styles.reasoningTitle}>Why These Recommendations?</Text>
              <Text style={styles.reasoningText}>{weatherData.reasoning}</Text>
              <View style={styles.sourceContainer}>
                <Text style={styles.sourceLabel}>Source: </Text>
                <Text style={styles.sourceText}>{weatherData.source}</Text>
              </View>
            </Card>

            {/* Forecast Card */}
            <Card style={styles.forecastCard}>
              <Text style={styles.forecastTitle}>3-Day Forecast</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.forecastScroll}>
                {weatherData.weather.forecast.map((day, index) => (
                  <View key={index} style={styles.forecastDay}>
                    <Text style={styles.forecastDate}>
                      {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                    </Text>
                    <Ionicons name={getWeatherIcon(day.icon, 'd')} size={32} color="#4169e1" />
                    <Text style={styles.forecastTemp}>
                      {day.temperature.min.toFixed(0)}° - {day.temperature.max.toFixed(0)}°C
                    </Text>
                    <Text style={styles.forecastDesc}>{day.description}</Text>
                    {day.precipitation_probability > 0 && (
                      <View style={styles.precipContainer}>
                        <Ionicons name="water" size={14} color="#4169e1" />
                        <Text style={styles.precipText}>{(day.precipitation_probability * 100).toFixed(0)}%</Text>
                      </View>
                    )}
                  </View>
                ))}
              </ScrollView>
            </Card>
          </>
        ) : (
          <View style={styles.errorContainer}>
            <Ionicons name="alert-circle" size={48} color="#ff4757" />
            <Text style={styles.errorText}>
              {weatherData ? weatherData.message || 'Failed to load weather data' : 'Loading weather data...'}
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  searchContainer: {
    backgroundColor: '#e3f2fd',
    padding: 16,
  },
  searchLabel: {
    fontSize: 16,
    marginBottom: 8,
    color: '#4169e1',
  },
  searchInputContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 8,
    overflow: 'hidden',
  },
  searchInput: {
    flex: 1,
    height: 48,
    paddingHorizontal: 16,
    fontSize: 16,
  },
  searchButton: {
    backgroundColor: '#4169e1',
    width: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  contentContainer: {
    flex: 1,
    padding: 16,
  },
  weatherCard: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
  },
  weatherHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  weatherLocation: {},
  cityName: {
    fontSize: 24,
    fontWeight: '600',
  },
  countryName: {
    fontSize: 16,
    color: '#555',
  },
  weatherDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  temperatureContainer: {},
  temperature: {
    fontSize: 36,
    fontWeight: '600',
  },
  feelsLike: {
    fontSize: 14,
    color: '#555',
  },
  conditionsContainer: {
    alignItems: 'flex-end',
  },
  weatherDescription: {
    fontSize: 16,
    textTransform: 'capitalize',
    marginBottom: 4,
  },
  weatherMetrics: {
    flexDirection: 'row',
  },
  metric: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 12,
  },
  metricText: {
    marginLeft: 4,
    fontSize: 14,
    color: '#555',
  },
  recommendationCard: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
  },
  recommendationTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  recommendationContent: {
    marginLeft: 12,
    flex: 1,
  },
  recommendationLabel: {
    fontSize: 14,
    color: '#555',
  },
  recommendationText: {
    fontSize: 16,
  },
  tipsCard: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
    backgroundColor: '#fffbea',
  },
  tipsTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tipText: {
    marginLeft: 8,
    fontSize: 14,
    flex: 1,
  },
  reasoningCard: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
  },
  reasoningTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  reasoningText: {
    fontSize: 14,
    lineHeight: 20,
    color: '#333',
    marginBottom: 12,
  },
  sourceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sourceLabel: {
    fontSize: 12,
    color: '#555',
  },
  sourceText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#4169e1',
  },
  forecastCard: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
  },
  forecastTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  forecastScroll: {
    flexDirection: 'row',
  },
  forecastDay: {
    alignItems: 'center',
    marginRight: 24,
    minWidth: 80,
  },
  forecastDate: {
    fontSize: 14,
    marginBottom: 8,
  },
  forecastTemp: {
    fontSize: 14,
    fontWeight: '500',
    marginTop: 4,
  },
  forecastDesc: {
    fontSize: 12,
    color: '#555',
    textTransform: 'capitalize',
    marginTop: 2,
  },
  precipContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  precipText: {
    fontSize: 12,
    color: '#4169e1',
    marginLeft: 2,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  errorText: {
    fontSize: 16,
    color: '#555',
    textAlign: 'center',
    marginTop: 16,
  },
});

export default WeatherScreen;
