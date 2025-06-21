import { Request, Response } from 'express';
import queryService from '../services/query.service';
import { ApiResponse, Restaurant } from '../types';

/**
 * QueryController - Handles HTTP requests for food queries
 */
class QueryController {
  /**
   * Process a natural language food query
   * @param req - Express request object
   * @param res - Express response object
   */
  async processQuery(req: Request, res: Response): Promise<void> {
    try {
      const { query, userId } = req.body;
      
      // Validate required fields
      if (!query) {
        res.status(400).json({
          success: false,
          error: 'Query is required'
        } as ApiResponse<null>);
        return;
      }
      
      // Process the query
      const results = await queryService.processQuery(query, userId);
      
      // Return the results
      res.status(200).json({
        success: true,
        data: results,
        message: `Found ${results.length} restaurants matching your query`
      } as ApiResponse<Restaurant[]>);
    } catch (error) {
      console.error('Error processing query:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to process query'
      } as ApiResponse<null>);
    }
  }
}

export default new QueryController();
