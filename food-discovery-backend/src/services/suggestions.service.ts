import foodAgent from '../agents/foodAgent';
import { Restaurant, SuggestionRequest } from '../types';

/**
 * SuggestionsService - Handles proactive food suggestions based on time, location, and preferences
 */
class SuggestionsService {
  /**
   * Generate proactive food suggestions
   * @param request - Suggestion request with user ID, location, and time
   * @returns List of suggested restaurants
   */
  async generateSuggestions(request: SuggestionRequest): Promise<Restaurant[]> {
    try {
      console.log(`Generating suggestions for user: ${request.userId}`);
      
      // Use the food agent to generate suggestions
      const suggestions = await foodAgent.generateSuggestions(
        request.userId,
        request.location,
        request.time
      );
      
      console.log(`Generated ${suggestions.length} suggestions`);
      return suggestions;
    } catch (error) {
      console.error('Error in suggestions service:', error);
      throw new Error('Failed to generate suggestions');
    }
  }
}

export default new SuggestionsService();
