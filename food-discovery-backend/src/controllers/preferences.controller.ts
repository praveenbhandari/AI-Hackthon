import { Request, Response } from 'express';
import preferencesService from '../services/preferences.service';
import { ApiResponse, UserPreference } from '../types';

/**
 * PreferencesController - Handles HTTP requests for user preferences
 */
class PreferencesController {
  /**
   * Get user preferences by user ID
   * @param req - Express request object
   * @param res - Express response object
   */
  async getUserPreferences(req: Request, res: Response): Promise<void> {
    try {
      const userId = req.params.userId;
      
      // Validate required fields
      if (!userId) {
        res.status(400).json({
          success: false,
          error: 'User ID is required'
        } as ApiResponse<null>);
        return;
      }
      
      // Get user preferences
      const preferences = await preferencesService.getUserPreferences(userId);
      
      if (!preferences) {
        res.status(404).json({
          success: false,
          error: 'User preferences not found'
        } as ApiResponse<null>);
        return;
      }
      
      // Return the preferences
      res.status(200).json({
        success: true,
        data: preferences,
        message: 'User preferences retrieved successfully'
      } as ApiResponse<UserPreference>);
    } catch (error) {
      console.error('Error getting user preferences:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get user preferences'
      } as ApiResponse<null>);
    }
  }

  /**
   * Save user preferences
   * @param req - Express request object
   * @param res - Express response object
   */
  async saveUserPreferences(req: Request, res: Response): Promise<void> {
    try {
      const preferences = req.body as UserPreference;
      
      // Validate required fields
      if (!preferences.userId) {
        res.status(400).json({
          success: false,
          error: 'User ID is required'
        } as ApiResponse<null>);
        return;
      }
      
      // Save user preferences
      const savedPreferences = await preferencesService.saveUserPreferences(preferences);
      
      // Return the saved preferences
      res.status(200).json({
        success: true,
        data: savedPreferences,
        message: 'User preferences saved successfully'
      } as ApiResponse<UserPreference>);
    } catch (error) {
      console.error('Error saving user preferences:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to save user preferences'
      } as ApiResponse<null>);
    }
  }
}

export default new PreferencesController();
