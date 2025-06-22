import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, ScrollView, Image, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card, Chip } from 'react-native-paper';
import { searchRestaurants } from '../api/foodApi'; // @ts-ignore - foodApi.js doesn't have type declarations

// Define types for our restaurant data
interface Restaurant {
  id: string;
  name: string;
  rating: number;
  price_level: number;
  distance: number;
  isOpen: boolean;
  categories: string[];
  image: string;
  dietary: string[];
}

// This would be replaced with actual API calls to your backend
const mockRestaurants: Restaurant[] = [
  {
    id: '1',
    name: 'Ramen House',
    rating: 4.2,
    price_level: 2,
    distance: 0.3,
    isOpen: true,
    categories: ['Japanese', 'Noodles'],
    image: 'https://via.placeholder.com/100?text=🍜',
    dietary: []
  },
  {
    id: '2',
    name: 'Tony\'s Pizza',
    rating: 4.8,
    price_level: 1,
    distance: 0.5,
    isOpen: true,
    categories: ['Italian', 'Pizza'],
    image: 'https://via.placeholder.com/100?text=🍕',
    dietary: []
  },
  {
    id: '3',
    name: 'Green Garden',
    rating: 4.0,
    price_level: 3,
    distance: 0.8,
    isOpen: false,
    categories: ['Salad', 'Healthy'],
    image: 'https://via.placeholder.com/100?text=🥗',
    dietary: ['Vegan']
  }
];

const FoodScreen = () => {
  const [query, setQuery] = useState('');
  const [restaurants, setRestaurants] = useState<Restaurant[]>(mockRestaurants);
  const [activeFilters, setActiveFilters] = useState(['$', '$$', 'Veg', 'Open now']);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Search for restaurants using the foodApi integration
  const handleSearchRestaurants = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      // Default to Berkeley if no specific location is mentioned
      const location = 'Berkeley, CA';
      const result = await searchRestaurants(searchQuery, location);
      
      if (result.success) {
        setRestaurants(result.restaurants);
      } else {
        setError(result.message || 'Failed to find restaurants');
      }
    } catch (err) {
      console.error('Error searching restaurants:', err);
      setError('An error occurred while searching for restaurants');
    } finally {
      setLoading(false);
    }
  };

  const toggleFilter = (filter: string) => {
    if (activeFilters.includes(filter)) {
      setActiveFilters(activeFilters.filter(f => f !== filter));
    } else {
      setActiveFilters([...activeFilters, filter]);
    }
  };

  const handleSearch = () => {
    handleSearchRestaurants(query);
  };

  const renderPriceLevel = (level: number) => {
    let priceText = '';
    for (let i = 0; i < level; i++) {
      priceText += '$';
    }
    return priceText;
  };

  const renderStars = (rating: number) => {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5;
    const stars = [];
    
    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<Ionicons key={i} name="star" size={16} color="#ffc107" />);
      } else if (i === fullStars && halfStar) {
        stars.push(<Ionicons key={i} name="star-half" size={16} color="#ffc107" />);
      } else {
        stars.push(<Ionicons key={i} name="star-outline" size={16} color="#ffc107" />);
      }
    }
    
    return <View style={styles.starsContainer}>{stars}</View>;
  };

  return (
    <View style={styles.container}>
      {/* Search Section */}
      <View style={styles.searchContainer}>
        <Text style={styles.searchLabel}>What are you craving?</Text>
        <View style={styles.searchInputContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Search for restaurants, cuisines, or dishes"
            value={query}
            onChangeText={setQuery}
          />
          <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
            <Ionicons name="search" size={20} color="#555" />
          </TouchableOpacity>
        </View>
        
        {/* Filters */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filtersContainer}>
          <TouchableOpacity 
            style={[styles.filterChip, activeFilters.includes('$') && styles.activeFilterChip]} 
            onPress={() => toggleFilter('$')}
          >
            <Text style={[styles.filterText, activeFilters.includes('$') && styles.activeFilterText]}>$</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.filterChip, activeFilters.includes('$$') && styles.activeFilterChip]} 
            onPress={() => toggleFilter('$$')}
          >
            <Text style={[styles.filterText, activeFilters.includes('$$') && styles.activeFilterText]}>$$</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.filterChip, activeFilters.includes('$$$') && styles.activeFilterChip]} 
            onPress={() => toggleFilter('$$$')}
          >
            <Text style={[styles.filterText, activeFilters.includes('$$$') && styles.activeFilterText]}>$$$</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.filterChip, activeFilters.includes('Veg') && styles.activeFilterChip]} 
            onPress={() => toggleFilter('Veg')}
          >
            <Text style={[styles.filterText, activeFilters.includes('Veg') && styles.activeFilterText]}>Veg</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.filterChip, activeFilters.includes('Open now') && styles.activeFilterChip]} 
            onPress={() => toggleFilter('Open now')}
          >
            <Text style={[styles.filterText, activeFilters.includes('Open now') && styles.activeFilterText]}>Open now</Text>
          </TouchableOpacity>
        </ScrollView>
      </View>

      {/* Restaurant List */}
      <ScrollView style={styles.restaurantsContainer}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#4cd137" />
            <Text style={styles.loadingText}>Finding the best restaurants...</Text>
          </View>
        ) : error ? (
          <View style={styles.errorContainer}>
            <Ionicons name="alert-circle" size={48} color="#ff4757" />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : restaurants.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="restaurant" size={48} color="#555" />
            <Text style={styles.emptyText}>Search for restaurants to see results</Text>
          </View>
        ) : (
          <>
            {restaurants.map((restaurant) => (
              <Card key={restaurant.id} style={styles.restaurantCard}>
                <View style={styles.restaurantCardContent}>
                  <View style={styles.restaurantImageContainer}>
                    <Image source={{ uri: restaurant.image }} style={styles.restaurantImage} />
                  </View>
                  <View style={styles.restaurantInfo}>
                    <View style={styles.restaurantHeader}>
                      <Text style={styles.restaurantName}>{restaurant.name}</Text>
                      <Text style={restaurant.isOpen ? styles.openStatus : styles.closedStatus}>
                        {restaurant.isOpen ? 'Open' : 'Closed'}
                      </Text>
                    </View>
                    <View style={styles.restaurantRating}>
                      {renderStars(restaurant.rating)}
                      <Text style={styles.ratingText}>{restaurant.rating}</Text>
                    </View>
                    <View style={styles.restaurantDetails}>
                      <Text style={styles.priceLevel}>
                        {renderPriceLevel(restaurant.price_level)}
                      </Text>
                      <Text style={styles.distance}>• {restaurant.distance} miles</Text>
                      {restaurant.dietary.length > 0 && (
                        <Text style={styles.dietary}>• {restaurant.dietary.join(', ')}</Text>
                      )}
                    </View>
                  </View>
                </View>
              </Card>
            ))}
          </>
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
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e4e8',
  },
  searchLabel: {
    fontSize: 16,
    marginBottom: 8,
    color: '#333',
  },
  searchInputContainer: {
    flexDirection: 'row',
    backgroundColor: '#f5f7fa',
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 12,
  },
  searchInput: {
    flex: 1,
    height: 48,
    paddingHorizontal: 16,
    fontSize: 16,
  },
  searchButton: {
    width: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  filtersContainer: {
    flexDirection: 'row',
    paddingVertical: 8,
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f5f7fa',
    marginRight: 8,
  },
  activeFilterChip: {
    backgroundColor: '#4cd137',
  },
  filterText: {
    color: '#555',
  },
  activeFilterText: {
    color: '#fff',
  },
  restaurantsContainer: {
    flex: 1,
    padding: 16,
  },
  restaurantCard: {
    marginBottom: 16,
    borderRadius: 8,
  },
  restaurantCardContent: {
    flexDirection: 'row',
    padding: 12,
  },
  restaurantImageContainer: {
    width: 70,
    height: 70,
    borderRadius: 8,
    overflow: 'hidden',
    backgroundColor: '#f5f7fa',
    marginRight: 12,
  },
  restaurantImage: {
    width: '100%',
    height: '100%',
  },
  restaurantInfo: {
    flex: 1,
  },
  restaurantHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  restaurantName: {
    fontSize: 18,
    fontWeight: '600',
  },
  openStatus: {
    fontSize: 12,
    color: '#4cd137',
    fontWeight: '500',
  },
  closedStatus: {
    fontSize: 12,
    color: '#ff4757',
    fontWeight: '500',
  },
  restaurantRating: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  starsContainer: {
    flexDirection: 'row',
    marginRight: 4,
  },
  ratingText: {
    fontSize: 14,
    color: '#555',
  },
  restaurantDetails: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  priceLevel: {
    fontSize: 14,
    color: '#555',
  },
  distance: {
    fontSize: 14,
    color: '#555',
    marginLeft: 4,
  },
  dietary: {
    fontSize: 14,
    color: '#4cd137',
  },
  loadingContainer: {
    padding: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#555',
  },
  errorContainer: {
    padding: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorText: {
    marginTop: 16,
    fontSize: 16,
    color: '#ff4757',
    textAlign: 'center',
  },
  emptyContainer: {
    padding: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
    color: '#555',
    textAlign: 'center',
  },
});

export default FoodScreen;
