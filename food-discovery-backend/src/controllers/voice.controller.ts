import { Request, Response } from 'express';
import voiceService from '../services/voice.service';
import { ApiResponse, Restaurant, VoiceInput } from '../types';

/**
 * VoiceController - Handles HTTP requests for voice transcriptions
 */
class VoiceController {
  /**
   * Process a voice transcription for food recommendations
   * @param req - Express request object
   * @param res - Express response object
   */
  async processVoiceQuery(req: Request, res: Response): Promise<void> {
    try {
      const voiceInput = req.body as VoiceInput;
      
      // Validate required fields
      if (!voiceInput.userId || !voiceInput.transcription) {
        res.status(400).json({
          success: false,
          error: 'User ID and transcription are required'
        } as ApiResponse<null>);
        return;
      }
      
      // Process the voice query
      const results = await voiceService.processVoiceQuery(voiceInput);
      
      // Return the results
      res.status(200).json({
        success: true,
        data: results,
        message: `Found ${results.length} restaurants matching your voice query`
      } as ApiResponse<Restaurant[]>);
    } catch (error) {
      console.error('Error processing voice query:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to process voice query'
      } as ApiResponse<null>);
    }
  }
}

export default new VoiceController();
