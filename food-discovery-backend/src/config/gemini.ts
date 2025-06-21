import { GoogleGenerativeAI } from '@google/generative-ai';
import dotenv from 'dotenv';

dotenv.config();

// Check if the required environment variables are set
if (!process.env.GOOGLE_GEMINI_API_KEY) {
  console.error('Missing Google Gemini API key. Please check your .env file.');
  process.exit(1);
}

// Initialize the Google Generative AI client
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_GEMINI_API_KEY);

// Get the model
const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

export { genAI, model };
