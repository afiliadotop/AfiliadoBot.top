import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Security check: Never use service_role_key (starting with sb_secret_) in the frontend
const isSecretKey = supabaseAnonKey?.startsWith('sb_secret_');

if (isSecretKey) {
  console.error('CRITICAL SECURITY ERROR: Supabase Service Role Key detected in Frontend!');
}

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase credentials missing in Frontend environment');
}

export const supabase = createClient(supabaseUrl || '', (isSecretKey ? '' : supabaseAnonKey) || '');
