import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';

// Import screens
import SafetyScreen from './screens/SafetyScreen';
import TransportScreen from './screens/TransportScreen';
import FoodScreen from './screens/FoodScreen';
import WeatherScreen from './screens/WeatherScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <StatusBar style="auto" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName;

              if (route.name === 'Safety') {
                iconName = focused ? 'shield' : 'shield-outline';
              } else if (route.name === 'Transport') {
                iconName = focused ? 'bus' : 'bus-outline';
              } else if (route.name === 'Food') {
                iconName = focused ? 'restaurant' : 'restaurant-outline';
              } else if (route.name === 'Weather') {
                iconName = focused ? 'partly-sunny' : 'partly-sunny-outline';
              }

              return <Ionicons name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#4169e1',
            tabBarInactiveTintColor: 'gray',
            headerShown: true,
            headerTitle: 'NavLife',
            headerTitleStyle: {
              fontWeight: 'bold',
              color: '#4169e1',
            },
            headerStyle: {
              elevation: 0,
              shadowOpacity: 0,
              borderBottomWidth: 0,
            },
          })}
        >
          <Tab.Screen name="Safety" component={SafetyScreen} />
          <Tab.Screen name="Transport" component={TransportScreen} />
          <Tab.Screen name="Food" component={FoodScreen} />
          <Tab.Screen name="Weather" component={WeatherScreen} />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
