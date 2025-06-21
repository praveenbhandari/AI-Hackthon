import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';

// Import routes
import {
  queryRouter,
  preferencesRouter,
  feedbackRouter,
  voiceRouter,
  suggestionsRouter
} from './routes';

// Import middleware
import { errorHandler, requestLogger } from './middleware/errorMiddleware';

// Load environment variables
dotenv.config();

// Create Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(requestLogger);

// Routes
app.use('/query', queryRouter);
app.use('/preferences', preferencesRouter);
app.use('/feedback', feedbackRouter);
app.use('/voice', voiceRouter);
app.use('/suggestions', suggestionsRouter);

// Root path handler - API documentation or redirect
app.get('/', (req: Request, res: Response) => {
  res.status(200).json({
    status: 'ok',
    message: 'Food Discovery API',
    description: 'Backend API for the Food Discovery feature',
    documentation: 'See README.md for API documentation',
    endpoints: [
      { method: 'GET', path: '/health', description: 'Health check endpoint' },
      { method: 'POST', path: '/query', description: 'Process natural language food queries' },
      { method: 'GET', path: '/preferences/:userId', description: 'Get user preferences' },
      { method: 'POST', path: '/preferences', description: 'Save user preferences' },
      { method: 'POST', path: '/feedback', description: 'Save user feedback' },
      { method: 'GET', path: '/feedback/restaurant/:restaurantId', description: 'Get feedback for a restaurant' },
      { method: 'GET', path: '/feedback/user/:userId', description: 'Get feedback from a user' },
      { method: 'POST', path: '/voice', description: 'Process voice input' },
      { method: 'POST', path: '/suggestions', description: 'Get proactive suggestions' }
    ],
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  res.status(200).json({
    status: 'ok',
    message: 'Food Discovery API is running',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// Error handling middleware
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log('Available endpoints:');
  console.log('- GET  /health');
  console.log('- POST /query');
  console.log('- GET  /preferences/:userId');
  console.log('- POST /preferences');
  console.log('- POST /feedback');
  console.log('- GET  /feedback/restaurant/:restaurantId');
  console.log('- GET  /feedback/user/:userId');
  console.log('- POST /voice');
  console.log('- POST /suggestions');
});

export default app;
