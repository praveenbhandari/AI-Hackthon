import queryService from './query.service';
import { Restaurant, VoiceInput } from '../types';

/**
 * VoiceService - Handles processing of voice transcriptions for food queries
 */
class VoiceService {
  /**
   * Process a voice transcription for food recommendations
   * @param voiceInput - Voice input with transcription and user ID
   * @returns List of restaurant recommendations
   */
  async processVoiceQuery(voiceInput: VoiceInput): Promise<Restaurant[]> {
    try {
      console.log(`Processing voice query: "${voiceInput.transcription}" for user: ${voiceInput.userId}`);
      
      // Use the query service to process the transcribed text
      // This reuses the same logic as the /query endpoint
      const results = await queryService.processQuery(
        voiceInput.transcription, 
        voiceInput.userId
      );
      
      console.log(`Found ${results.length} results for voice query`);
      return results;
    } catch (error) {
      console.error('Error in voice service:', error);
      throw new Error('Failed to process voice query');
    }
  }
}

export default new VoiceService();
