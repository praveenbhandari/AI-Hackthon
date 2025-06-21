import { Response } from 'express';
import { ApiResponse } from '../types';

/**
 * Send a success response
 * @param res - Express response object
 * @param data - Data to send in the response
 * @param message - Success message
 * @param statusCode - HTTP status code (default: 200)
 */
export const sendSuccessResponse = <T>(
  res: Response,
  data: T,
  message = 'Operation successful',
  statusCode = 200
): void => {
  res.status(statusCode).json({
    success: true,
    data,
    message,
  } as ApiResponse<T>);
};

/**
 * Send an error response
 * @param res - Express response object
 * @param error - Error message
 * @param statusCode - HTTP status code (default: 500)
 */
export const sendErrorResponse = (
  res: Response,
  error: string,
  statusCode = 500
): void => {
  res.status(statusCode).json({
    success: false,
    error,
  } as ApiResponse<null>);
};

/**
 * Logger utility for consistent logging
 */
export const logger = {
  info: (message: string, data?: any): void => {
    console.log(`[INFO] ${message}`, data ? data : '');
  },
  
  error: (message: string, error?: any): void => {
    console.error(`[ERROR] ${message}`, error ? error : '');
  },
  
  warn: (message: string, data?: any): void => {
    console.warn(`[WARN] ${message}`, data ? data : '');
  },
  
  debug: (message: string, data?: any): void => {
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`, data ? data : '');
    }
  },
};
