import { Request, Response } from 'express';
import suggestionsService from '../services/suggestions.service';
import { ApiResponse, Restaurant, SuggestionRequest } from '../types';

/**
 * SuggestionsController - Handles HTTP requests for proactive food suggestions
 */
class SuggestionsController {
  /**
   * Generate proactive food suggestions
   * @param req - Express request object
   * @param res - Express response object
   */
  async generateSuggestions(req: Request, res: Response): Promise<void> {
    try {
      const request = req.body as SuggestionRequest;
      
      // Validate required fields
      if (!request.userId) {
        res.status(400).json({
          success: false,
          error: 'User ID is required'
        } as ApiResponse<null>);
        return;
      }
      
      // Generate suggestions
      const suggestions = await suggestionsService.generateSuggestions(request);
      
      // Return the suggestions
      res.status(200).json({
        success: true,
        data: suggestions,
        message: `Generated ${suggestions.length} restaurant suggestions`
      } as ApiResponse<Restaurant[]>);
    } catch (error) {
      console.error('Error generating suggestions:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to generate suggestions'
      } as ApiResponse<null>);
    }
  }
}

export default new SuggestionsController();
