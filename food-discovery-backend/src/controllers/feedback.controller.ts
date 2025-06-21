import { Request, Response } from 'express';
import feedbackService from '../services/feedback.service';
import { ApiResponse, Feedback } from '../types';

/**
 * FeedbackController - Handles HTTP requests for user feedback
 */
class FeedbackController {
  /**
   * Save user feedback for a restaurant
   * @param req - Express request object
   * @param res - Express response object
   */
  async saveFeedback(req: Request, res: Response): Promise<void> {
    try {
      const feedback = req.body as Feedback;
      
      // Validate required fields
      if (!feedback.userId || !feedback.restaurantId || feedback.rating === undefined) {
        res.status(400).json({
          success: false,
          error: 'User ID, restaurant ID, and rating are required'
        } as ApiResponse<null>);
        return;
      }
      
      // Save feedback
      const savedFeedback = await feedbackService.saveFeedback(feedback);
      
      // Return the saved feedback
      res.status(201).json({
        success: true,
        data: savedFeedback,
        message: 'Feedback saved successfully'
      } as ApiResponse<Feedback>);
    } catch (error) {
      console.error('Error saving feedback:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to save feedback'
      } as ApiResponse<null>);
    }
  }

  /**
   * Get all feedback for a specific restaurant
   * @param req - Express request object
   * @param res - Express response object
   */
  async getRestaurantFeedback(req: Request, res: Response): Promise<void> {
    try {
      const restaurantId = req.params.restaurantId;
      
      // Validate required fields
      if (!restaurantId) {
        res.status(400).json({
          success: false,
          error: 'Restaurant ID is required'
        } as ApiResponse<null>);
        return;
      }
      
      // Get restaurant feedback
      const feedback = await feedbackService.getRestaurantFeedback(restaurantId);
      
      // Return the feedback
      res.status(200).json({
        success: true,
        data: feedback,
        message: `Retrieved ${feedback.length} feedback items for restaurant`
      } as ApiResponse<Feedback[]>);
    } catch (error) {
      console.error('Error getting restaurant feedback:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get restaurant feedback'
      } as ApiResponse<null>);
    }
  }

  /**
   * Get all feedback from a specific user
   * @param req - Express request object
   * @param res - Express response object
   */
  async getUserFeedback(req: Request, res: Response): Promise<void> {
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
      
      // Get user feedback
      const feedback = await feedbackService.getUserFeedback(userId);
      
      // Return the feedback
      res.status(200).json({
        success: true,
        data: feedback,
        message: `Retrieved ${feedback.length} feedback items from user`
      } as ApiResponse<Feedback[]>);
    } catch (error) {
      console.error('Error getting user feedback:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get user feedback'
      } as ApiResponse<null>);
    }
  }
}

export default new FeedbackController();
