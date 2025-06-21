/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  statusCode: number;
  
  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
    this.name = 'ApiError';
  }
}

/**
 * Format error response for API
 * @param error - Error object
 * @returns Formatted error object
 */
export const formatError = (error: Error | ApiError): { message: string; statusCode?: number } => {
  return {
    message: error.message || 'An unexpected error occurred',
    statusCode: (error as ApiError).statusCode || 500,
  };
};

/**
 * Validate required fields in a request
 * @param obj - Object to validate
 * @param requiredFields - Array of required field names
 * @throws ApiError if any required field is missing
 */
export const validateRequiredFields = (obj: Record<string, any>, requiredFields: string[]): void => {
  const missingFields = requiredFields.filter(field => !obj[field]);
  
  if (missingFields.length > 0) {
    throw new ApiError(`Missing required fields: ${missingFields.join(', ')}`, 400);
  }
};
