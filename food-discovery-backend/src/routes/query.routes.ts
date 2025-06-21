import { Router } from 'express';
import queryController from '../controllers/query.controller';

const router = Router();

/**
 * @route POST /query
 * @desc Process natural language food query
 * @access Public
 */
router.post('/', queryController.processQuery);

export { router as queryRouter };
