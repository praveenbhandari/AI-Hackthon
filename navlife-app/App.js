import React from 'react';
import { StyleSheet, Text, View, SafeAreaView } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

// Create a simple placeholder component for screens that aren't fully implemented
const PlaceholderScreen = ({ title }) => (
  <View style={styles.container}>
    <Text style={styles.title}>{title}</Text>
    <Text style={styles.subtitle}>This feature is coming soon!</Text>
  </View>
);

// Weather Screen Component
const WeatherScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>Weather</Text>
    <Text style={styles.subtitle}>Current Weather: Clear Sky</Text>
    <Text style={styles.content}>Temperature: 68°F</Text>
    <Text style={styles.content}>Recommendation: Light jacket</Text>
  </View>
);

// Food Screen Component
const FoodScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>Food Discovery</Text>
    <Text style={styles.subtitle}>Find restaurants near you</Text>
    <Text style={styles.content}>Try searching for "Mexican restaurants near me"</Text>
  </View>
);

// Create the tab navigator
const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;

            if (route.name === 'Weather') {
              iconName = focused ? 'sunny' : 'sunny-outline';
            } else if (route.name === 'Food') {
              iconName = focused ? 'restaurant' : 'restaurant-outline';
            } else if (route.name === 'Transport') {
              iconName = focused ? 'car' : 'car-outline';
            } else if (route.name === 'Safety') {
              iconName = focused ? 'shield-checkmark' : 'shield-checkmark-outline';
            }

            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#4cd137',
          tabBarInactiveTintColor: 'gray',
        })}
      >
        <Tab.Screen name="Weather" component={WeatherScreen} />
        <Tab.Screen name="Food" component={FoodScreen} />
        <Tab.Screen 
          name="Transport" 
          component={() => <PlaceholderScreen title="Transport" />} 
        />
        <Tab.Screen 
          name="Safety" 
          component={() => <PlaceholderScreen title="Safety" />} 
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 18,
    marginBottom: 20,
    color: '#555',
  },
  content: {
    fontSize: 16,
    marginBottom: 10,
    color: '#666',
  },
});
