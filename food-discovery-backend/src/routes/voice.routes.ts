import { Router } from 'express';
import voiceController from '../controllers/voice.controller';

const router = Router();

/**
 * @route POST /voice
 * @desc Process a voice transcription for food recommendations
 * @access Public
 */
router.post('/', voiceController.processVoiceQuery);

export { router as voiceRouter };
