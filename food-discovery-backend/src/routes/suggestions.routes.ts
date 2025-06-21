import { Router } from 'express';
import suggestionsController from '../controllers/suggestions.controller';

const router = Router();

/**
 * @route POST /suggestions
 * @desc Generate proactive food suggestions based on time, location, and preferences
 * @access Public
 */
router.post('/', suggestionsController.generateSuggestions);

export { router as suggestionsRouter };
