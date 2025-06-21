import foodAgent from '../agents/foodAgent';
import { Restaurant } from '../types';

/**
 * QueryService - Handles processing of natural language food queries
 */
class QueryService {
  /**
   * Process a natural language query for food recommendations
   * @param query - Natural language query from user
   * @param userId - Optional user ID for personalized results
   * @returns List of restaurant recommendations
   */
  async processQuery(query: string, userId?: string): Promise<Restaurant[]> {
    try {
      console.log(`Processing query: "${query}" for user: ${userId || 'anonymous'}`);
      
      // Use the food agent to process the query
      const results = await foodAgent.processQuery(query, userId);
      
      console.log(`Found ${results.length} results for query`);
      return results;
    } catch (error) {
      console.error('Error in query service:', error);
      throw new Error('Failed to process food query');
    }
  }
}

export default new QueryService();
