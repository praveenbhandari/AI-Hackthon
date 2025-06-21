// User preferences types
export interface UserPreference {
  userId: string;
  dietaryRestrictions?: string[];
  cuisinePreferences?: string[];
  priceRange?: PriceRange;
  spicyLevel?: number; // 0-5 scale
  favoriteRestaurants?: string[];
  avoidRestaurants?: string[];
  createdAt: Date;
  updatedAt: Date;
}

// Price range enum (corresponds to Google Places price levels)
export enum PriceRange {
  Free = 0,
  Inexpensive = 1,
  Moderate = 2,
  Expensive = 3,
  VeryExpensive = 4
}

// Query parameters extracted from natural language
export interface QueryParams {
  cuisine?: string;
  priceLevel?: PriceRange;
  location?: string;
  openNow?: boolean;
  distance?: number; // in meters
  keywords?: string[];
}

// Restaurant/place information
export interface Restaurant {
  id: string;
  name: string;
  address: string;
  priceLevel?: PriceRange;
  cuisine?: string[];
  isOpen?: boolean;
  openingHours?: OpeningHours[];
  distance?: number;
  rating?: number;
  userRatingsTotal?: number;
  photos?: string[];
  website?: string;
  phoneNumber?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
}

// Opening hours structure
export interface OpeningHours {
  day: number; // 0 = Sunday, 6 = Saturday
  openTime: string; // 24-hour format, e.g., "09:00"
  closeTime: string; // 24-hour format, e.g., "21:00"
}

// Feedback from users
export interface Feedback {
  id?: string;
  userId: string;
  restaurantId: string;
  rating: number; // 1-5 scale
  thumbsUp?: boolean;
  comment?: string;
  createdAt: Date;
}

// Voice input
export interface VoiceInput {
  userId: string;
  transcription: string;
}

// Suggestion request
export interface SuggestionRequest {
  userId: string;
  location?: {
    lat: number;
    lng: number;
  };
  time?: Date;
}

// API response structure
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
