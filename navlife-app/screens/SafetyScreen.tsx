import React, { useState } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, Switch } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import MapView from 'react-native-maps';
import { Card, Button } from 'react-native-paper';

const SafetyScreen = () => {
  const [fromLocation, setFromLocation] = useState('');
  const [toLocation, setToLocation] = useState('');
  const [liveTracking, setLiveTracking] = useState(false);
  const [safetyScore, setSafetyScore] = useState(8.5);
  const [nearestPolice, setNearestPolice] = useState(0.3);

  const handleGetSafeRoute = () => {
    // This would connect to your backend safety API
    console.log('Getting safe route from', fromLocation, 'to', toLocation);
    // For demo purposes, we'll just set some dummy data
    setSafetyScore(8.5);
    setNearestPolice(0.3);
  };

  const handleShareLocation = () => {
    console.log('Sharing location with emergency contacts');
    // This would trigger your location sharing functionality
  };

  return (
    <View style={styles.container}>
      {/* Input Section */}
      <View style={styles.inputSection}>
        <View style={styles.inputContainer}>
          <Ionicons name="location" size={20} color="#4169e1" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="From"
            value={fromLocation}
            onChangeText={setFromLocation}
          />
        </View>
        
        <View style={styles.inputContainer}>
          <Ionicons name="location" size={20} color="#ff4757" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="To"
            value={toLocation}
            onChangeText={setToLocation}
          />
        </View>

        <TouchableOpacity 
          style={styles.getRouteButton}
          onPress={handleGetSafeRoute}
        >
          <Text style={styles.getRouteButtonText}>Get Safe Route</Text>
        </TouchableOpacity>
      </View>

      {/* Map Section */}
      <View style={styles.mapContainer}>
        <MapView
          style={styles.map}
          initialRegion={{
            latitude: 37.78825,
            longitude: -122.4324,
            latitudeDelta: 0.0922,
            longitudeDelta: 0.0421,
          }}
        />
        <View style={styles.mapLegend}>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#4cd137' }]} />
            <Text>Safe</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#ffa502' }]} />
            <Text>Moderate</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#ff4757' }]} />
            <Text>High-risk</Text>
          </View>
        </View>
      </View>

      {/* Safety Score Card */}
      <View style={styles.cardsContainer}>
        <Card style={styles.card}>
          <Card.Content style={styles.scoreCardContent}>
            <Text style={styles.safetyScore}>{safetyScore}</Text>
            <Text style={styles.safetyScoreLabel}>Safety Score</Text>
          </Card.Content>
        </Card>

        {/* Police Proximity Card */}
        <Card style={styles.card}>
          <Card.Content style={styles.policeCardContent}>
            <Ionicons name="shield" size={32} color="#4169e1" />
            <View style={styles.policeInfo}>
              <Text style={styles.policeLabel}>Nearest Police</Text>
              <Text style={styles.policeDistance}>{nearestPolice} miles</Text>
            </View>
            <Button mode="contained" style={styles.callButton} labelStyle={styles.callButtonText}>
              Call
            </Button>
          </Card.Content>
        </Card>
      </View>

      {/* Emergency Share */}
      <Card style={styles.emergencyCard}>
        <Card.Content style={styles.emergencyContent}>
          <View>
            <Text style={styles.emergencyTitle}>Emergency Share</Text>
            <Text style={styles.emergencySubtitle}>Send location to contacts</Text>
          </View>
          <Button 
            mode="contained" 
            style={styles.shareButton}
            onPress={handleShareLocation}
          >
            Share
          </Button>
        </Card.Content>
      </Card>

      {/* Live Tracking */}
      <Card style={styles.trackingCard}>
        <Card.Content style={styles.trackingContent}>
          <View>
            <Text style={styles.trackingTitle}>Live Tracking</Text>
            <Text style={styles.trackingSubtitle}>Share real-time location</Text>
          </View>
          <Switch
            value={liveTracking}
            onValueChange={setLiveTracking}
            trackColor={{ false: '#767577', true: '#4169e1' }}
            thumbColor={liveTracking ? '#f5f5f5' : '#f4f3f4'}
          />
        </Card.Content>
      </Card>

      {/* Safety Tips */}
      <Card style={styles.tipsCard}>
        <Card.Content>
          <View style={styles.tipsHeader}>
            <Ionicons name="bulb" size={24} color="#ffa502" />
            <Text style={styles.tipsTitle}>Safety Tips</Text>
          </View>
          <Text style={styles.tipText}>
            Stay in well-lit areas and avoid shortcuts through isolated places.
          </Text>
        </Card.Content>
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
    padding: 16,
  },
  inputSection: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    backgroundColor: '#f5f7fa',
    borderRadius: 8,
    padding: 8,
  },
  inputIcon: {
    marginRight: 8,
  },
  input: {
    flex: 1,
    height: 40,
    fontSize: 16,
  },
  getRouteButton: {
    backgroundColor: '#4169e1',
    borderRadius: 8,
    padding: 14,
    alignItems: 'center',
    marginTop: 8,
  },
  getRouteButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  mapContainer: {
    height: 250,
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 16,
  },
  map: {
    width: '100%',
    height: '100%',
  },
  mapLegend: {
    position: 'absolute',
    bottom: 10,
    left: 10,
    right: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    borderRadius: 8,
    padding: 8,
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  legendColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 4,
  },
  cardsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  card: {
    flex: 1,
    marginHorizontal: 4,
  },
  scoreCardContent: {
    alignItems: 'center',
    padding: 8,
  },
  safetyScore: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#4cd137',
  },
  safetyScoreLabel: {
    fontSize: 14,
    color: '#555',
  },
  policeCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 8,
  },
  policeInfo: {
    flex: 1,
    marginLeft: 8,
  },
  policeLabel: {
    fontSize: 14,
    color: '#555',
  },
  policeDistance: {
    fontSize: 16,
    fontWeight: '500',
  },
  callButton: {
    backgroundColor: '#4169e1',
    borderRadius: 4,
    paddingVertical: 2,
    paddingHorizontal: 12,
  },
  callButtonText: {
    fontSize: 12,
  },
  emergencyCard: {
    backgroundColor: '#fff8f8',
    marginBottom: 16,
  },
  emergencyContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  emergencyTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ff4757',
  },
  emergencySubtitle: {
    fontSize: 12,
    color: '#555',
  },
  shareButton: {
    backgroundColor: '#ff4757',
  },
  trackingCard: {
    marginBottom: 16,
  },
  trackingContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  trackingTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  trackingSubtitle: {
    fontSize: 12,
    color: '#555',
  },
  tipsCard: {
    marginBottom: 16,
  },
  tipsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  tipText: {
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
  },
});

export default SafetyScreen;
