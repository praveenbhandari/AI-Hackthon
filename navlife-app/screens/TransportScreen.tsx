import React, { useState } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from 'react-native-paper';

const TransportScreen = () => {
  const [routeQuery, setRouteQuery] = useState('');
  const [routes, setRoutes] = useState([
    {
      type: 'fastest',
      icon: 'trophy',
      iconColor: '#ffc107',
      title: 'Fastest Option',
      method: 'BART + Bus',
      duration: '45 min',
      eta: '3:45 PM',
      details: []
    },
    {
      type: 'cheapest',
      icon: 'cash',
      iconColor: '#4cd137',
      title: 'Cheapest Option',
      method: 'Bus Only',
      cost: '$3.50',
      duration: '1h 15min',
      details: []
    },
    {
      type: 'eco',
      icon: 'leaf',
      iconColor: '#2ed573',
      title: 'Eco-Friendly',
      method: 'Electric Bus + Walk',
      duration: '55 min',
      co2Saved: '2.1 kg',
      details: []
    }
  ]);

  const handleSearch = () => {
    console.log('Searching for routes:', routeQuery);
    // This would connect to your backend transport API
  };

  return (
    <View style={styles.container}>
      {/* Search Input */}
      <View style={styles.searchContainer}>
        <Text style={styles.searchLabel}>Where are you going from and to?</Text>
        <View style={styles.searchInputContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="From SFO Airport to CSU East Bay"
            value={routeQuery}
            onChangeText={setRouteQuery}
          />
          <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
            <Ionicons name="send" size={20} color="#fff" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Routes List */}
      <ScrollView style={styles.routesContainer}>
        {/* Fastest Option */}
        <Card style={styles.routeCard}>
          <View style={styles.routeIconContainer}>
            <Ionicons name="trophy" size={24} color="#ffc107" style={styles.routeIcon} />
          </View>
          <View style={styles.routeContent}>
            <Text style={styles.routeTitle}>Fastest Option</Text>
            <Text style={styles.routeMethod}>BART + Bus</Text>
            <View style={styles.routeDetails}>
              <Text style={styles.routeLabel}>ETA</Text>
              <Text style={styles.routeValue}>3:45 PM</Text>
            </View>
            <View style={styles.routeDetails}>
              <Text style={styles.routeLabel}>Duration</Text>
              <Text style={styles.routeValue}>45 min</Text>
            </View>
          </View>
        </Card>

        {/* Cheapest Option */}
        <Card style={styles.routeCard}>
          <View style={styles.routeIconContainer}>
            <Ionicons name="cash" size={24} color="#4cd137" style={styles.routeIcon} />
          </View>
          <View style={styles.routeContent}>
            <Text style={styles.routeTitle}>Cheapest Option</Text>
            <Text style={styles.routeMethod}>Bus Only</Text>
            <View style={styles.routeDetails}>
              <Text style={styles.routeLabel}>Cost</Text>
              <Text style={styles.routeValue}>$3.50</Text>
            </View>
            <View style={styles.routeDetails}>
              <Text style={styles.routeLabel}>Duration</Text>
              <Text style={styles.routeValue}>1h 15min</Text>
            </View>
          </View>
        </Card>

        {/* Eco-Friendly Option */}
        <Card style={styles.routeCard}>
          <View style={styles.routeIconContainer}>
            <Ionicons name="leaf" size={24} color="#2ed573" style={styles.routeIcon} />
          </View>
          <View style={styles.routeContent}>
            <Text style={styles.routeTitle}>Eco-Friendly</Text>
            <Text style={styles.routeMethod}>Electric Bus + Walk</Text>
            <View style={styles.routeDetails}>
              <Text style={styles.routeLabel}>Duration</Text>
              <Text style={styles.routeValue}>55 min</Text>
            </View>
            <View style={styles.routeDetails}>
              <Text style={styles.routeLabel}>CO₂ Saved</Text>
              <Text style={[styles.routeValue, styles.ecoValue]}>2.1 kg</Text>
            </View>
          </View>
        </Card>

        {/* Transit Apps Section */}
        <View style={styles.transitAppsSection}>
          <Text style={styles.transitAppsTitle}>Open in Transit Apps</Text>
          <View style={styles.transitAppsContainer}>
            <TouchableOpacity style={[styles.transitAppButton, styles.bartButton]}>
              <Text style={styles.transitAppButtonText}>BART</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.transitAppButton, styles.acTransitButton]}>
              <Text style={styles.transitAppButtonText}>AC Transit</Text>
            </TouchableOpacity>
          </View>
        </View>
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
    backgroundColor: '#f0e7fe',
    padding: 16,
  },
  searchLabel: {
    fontSize: 16,
    marginBottom: 8,
    color: '#6c5ce7',
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
    backgroundColor: '#6c5ce7',
    width: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  routesContainer: {
    flex: 1,
    padding: 16,
  },
  routeCard: {
    flexDirection: 'row',
    marginBottom: 16,
    padding: 16,
    borderRadius: 8,
  },
  routeIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#f5f7fa',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  routeIcon: {},
  routeContent: {
    flex: 1,
  },
  routeTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  routeMethod: {
    fontSize: 16,
    marginBottom: 8,
  },
  routeDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  routeLabel: {
    fontSize: 14,
    color: '#555',
  },
  routeValue: {
    fontSize: 14,
    fontWeight: '500',
  },
  ecoValue: {
    color: '#2ed573',
  },
  transitAppsSection: {
    marginTop: 16,
    marginBottom: 32,
  },
  transitAppsTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 12,
  },
  transitAppsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  transitAppButton: {
    flex: 1,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 8,
    marginHorizontal: 4,
  },
  bartButton: {
    backgroundColor: '#0078d7',
  },
  acTransitButton: {
    backgroundColor: '#ff6b01',
  },
  transitAppButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
});

export default TransportScreen;
