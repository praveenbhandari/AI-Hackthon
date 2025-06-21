import { createClient, SupabaseClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

// Check if the required environment variables are set
const hasSupabaseCredentials = !!process.env.SUPABASE_URL && !!process.env.SUPABASE_KEY;
if (!hasSupabaseCredentials) {
  console.warn('Missing Supabase environment variables. Database features will be disabled.');
}

// Create a Supabase client with proper error handling
let supabase: SupabaseClient;

if (hasSupabaseCredentials) {
  const supabaseUrl = process.env.SUPABASE_URL as string;
  const supabaseKey = process.env.SUPABASE_KEY as string;
  supabase = createClient(supabaseUrl, supabaseKey);
} else {
  // Create a mock client that returns empty data for development purposes
  supabase = {
    from: () => ({
      select: () => ({
        eq: () => ({
          single: async () => ({ data: null, error: { message: 'Supabase not configured' } }),
          order: () => ({ data: [], error: { message: 'Supabase not configured' } }),
          data: [],
          error: { message: 'Supabase not configured' }
        }),
        data: [],
        error: { message: 'Supabase not configured' }
      }),
      insert: () => ({ data: null, error: { message: 'Supabase not configured' } }),
      update: () => ({
        eq: () => ({ data: null, error: { message: 'Supabase not configured' } })
      }),
      delete: () => ({
        eq: () => ({ data: null, error: { message: 'Supabase not configured' } })
      })
    })
  } as any;
}

export default supabase;
