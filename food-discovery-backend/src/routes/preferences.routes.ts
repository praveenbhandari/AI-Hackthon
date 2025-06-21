import { Router } from 'express';
import preferencesController from '../controllers/preferences.controller';

const router = Router();

/**
 * @route GET /preferences/:userId
 * @desc Get user preferences by user ID
 * @access Public
 */
router.get('/:userId', preferencesController.getUserPreferences);

/**
 * @route POST /preferences
 * @desc Save user preferences
 * @access Public
 */
router.post('/', preferencesController.saveUserPreferences);

export { router as preferencesRouter };
