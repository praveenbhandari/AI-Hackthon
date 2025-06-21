import supabase from '../config/supabase';
import { Feedback } from '../types';

/**
 * FeedbackService - Handles user feedback on restaurant recommendations
 */
class FeedbackService {
  /**
   * Save user feedback for a restaurant
   * @param feedback - Feedback data to save
   * @returns Saved feedback with ID
   */
  async saveFeedback(feedback: Feedback): Promise<Feedback> {
    try {
      console.log(`Saving feedback for restaurant ${feedback.restaurantId} from user ${feedback.userId}`);
      
      // Set timestamp
      feedback.createdAt = new Date();
      
      const { data, error } = await supabase
        .from('feedback')
        .insert(feedback)
        .select()
        .single();
      
      if (error) {
        console.error('Error saving feedback:', error);
        throw new Error('Failed to save feedback');
      }
      
      return data as unknown as Feedback;
    } catch (error) {
      console.error('Error in feedback service:', error);
      throw new Error('Failed to save feedback');
    }
  }

  /**
   * Get all feedback for a specific restaurant
   * @param restaurantId - Restaurant ID to get feedback for
   * @returns List of feedback items
   */
  async getRestaurantFeedback(restaurantId: string): Promise<Feedback[]> {
    try {
      console.log(`Fetching feedback for restaurant: ${restaurantId}`);
      
      const { data, error } = await supabase
        .from('feedback')
        .select('*')
        .eq('restaurantId', restaurantId)
        .order('createdAt', { ascending: false });
      
      if (error) {
        console.error('Error fetching restaurant feedback:', error);
        throw new Error('Failed to fetch restaurant feedback');
      }
      
      return data as unknown as Feedback[];
    } catch (error) {
      console.error('Error in feedback service:', error);
      throw new Error('Failed to fetch restaurant feedback');
    }
  }

  /**
   * Get all feedback from a specific user
   * @param userId - User ID to get feedback for
   * @returns List of feedback items
   */
  async getUserFeedback(userId: string): Promise<Feedback[]> {
    try {
      console.log(`Fetching feedback from user: ${userId}`);
      
      const { data, error } = await supabase
        .from('feedback')
        .select('*')
        .eq('userId', userId)
        .order('createdAt', { ascending: false });
      
      if (error) {
        console.error('Error fetching user feedback:', error);
        throw new Error('Failed to fetch user feedback');
      }
      
      return data as unknown as Feedback[];
    } catch (error) {
      console.error('Error in feedback service:', error);
      throw new Error('Failed to fetch user feedback');
    }
  }
}

export default new FeedbackService();
