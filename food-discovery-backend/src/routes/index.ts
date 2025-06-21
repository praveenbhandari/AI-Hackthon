import { Router } from 'express';
import { queryRouter } from './query.routes';
import { preferencesRouter } from './preferences.routes';
import { feedbackRouter } from './feedback.routes';
import { voiceRouter } from './voice.routes';
import { suggestionsRouter } from './suggestions.routes';

// Export all routes for use in the main app
export {
  queryRouter,
  preferencesRouter,
  feedbackRouter,
  voiceRouter,
  suggestionsRouter
};
