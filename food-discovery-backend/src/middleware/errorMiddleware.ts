import { Request, Response, NextFunction } from 'express';
import { ApiError } from '../utils/errorHandler';
import { logger } from '../utils/apiUtils';

/**
 * Error handling middleware
 * @param err - Error object
 * @param req - Express request object
 * @param res - Express response object
 * @param next - Express next function
 */
export const errorHandler = (
  err: Error | ApiError,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const statusCode = (err as ApiError).statusCode || 500;
  const message = err.message || 'Internal Server Error';
  
  logger.error(`Error: ${message}`, err);
  
  res.status(statusCode).json({
    success: false,
    error: message
  });
};

/**
 * Request logging middleware
 * @param req - Express request object
 * @param res - Express response object
 * @param next - Express next function
 */
export const requestLogger = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const start = Date.now();
  
  logger.info(`${req.method} ${req.originalUrl}`);
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info(`${req.method} ${req.originalUrl} ${res.statusCode} - ${duration}ms`);
  });
  
  next();
};
