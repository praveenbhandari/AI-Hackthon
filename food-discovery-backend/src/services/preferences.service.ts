import supabase from '../config/supabase';
import { UserPreference } from '../types';

/**
 * PreferencesService - Handles user food preferences
 */
class PreferencesService {
  /**
   * Get user preferences by user ID
   * @param userId - User ID to fetch preferences for
   * @returns User preferences or null if not found
   */
  async getUserPreferences(userId: string): Promise<UserPreference | null> {
    try {
      console.log(`Fetching preferences for user: ${userId}`);
      
      const { data, error } = await supabase
        .from('preferences')
        .select('*')
        .eq('userId', userId)
        .single();
      
      if (error) {
        console.error('Error fetching user preferences:', error);
        return null;
      }
      
      return data as unknown as UserPreference;
    } catch (error) {
      console.error('Error in preferences service:', error);
      throw new Error('Failed to fetch user preferences');
    }
  }

  /**
   * Create or update user preferences
   * @param preferences - User preferences to save
   * @returns Updated user preferences
   */
  async saveUserPreferences(preferences: UserPreference): Promise<UserPreference> {
    try {
      console.log(`Saving preferences for user: ${preferences.userId}`);
      
      // Check if preferences already exist for this user
      const { data: existingPrefs } = await supabase
        .from('preferences')
        .select('*')
        .eq('userId', preferences.userId)
        .single();
      
      // Set timestamps
      const now = new Date();
      preferences.updatedAt = now;
      
      let result;
      
      if (existingPrefs) {
        // Update existing preferences
        const { data, error } = await supabase
          .from('preferences')
          .update(preferences)
          .eq('userId', preferences.userId)
          .select()
          .single();
        
        if (error) {
          console.error('Error updating user preferences:', error);
          throw new Error('Failed to update user preferences');
        }
        
        result = data;
      } else {
        // Create new preferences
        preferences.createdAt = now;
        
        const { data, error } = await supabase
          .from('preferences')
          .insert(preferences)
          .select()
          .single();
        
        if (error) {
          console.error('Error creating user preferences:', error);
          throw new Error('Failed to create user preferences');
        }
        
        result = data;
      }
      
      return result as unknown as UserPreference;
    } catch (error) {
      console.error('Error in preferences service:', error);
      throw new Error('Failed to save user preferences');
    }
  }
}

export default new PreferencesService();
