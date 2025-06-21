import { Router } from 'express';
import feedbackController from '../controllers/feedback.controller';

const router = Router();

/**
 * @route POST /feedback
 * @desc Save user feedback for a restaurant
 * @access Public
 */
router.post('/', feedbackController.saveFeedback);

/**
 * @route GET /feedback/restaurant/:restaurantId
 * @desc Get all feedback for a specific restaurant
 * @access Public
 */
router.get('/restaurant/:restaurantId', feedbackController.getRestaurantFeedback);

/**
 * @route GET /feedback/user/:userId
 * @desc Get all feedback from a specific user
 * @access Public
 */
router.get('/user/:userId', feedbackController.getUserFeedback);

export { router as feedbackRouter };
