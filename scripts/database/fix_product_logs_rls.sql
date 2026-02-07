-- Fix RLS Policy for product_logs table  
-- Allows service_role (used by scripts) to insert product change logs

-- Drop existing restrictive policies if any
DROP POLICY IF EXISTS "Service role can insert product logs" ON public.product_logs;
DROP POLICY IF EXISTS "Enable insert for service role" ON public.product_logs;
DROP POLICY IF EXISTS "Users can read product logs" ON public.product_logs;

-- Create policy to allow service_role to insert
CREATE POLICY "Service role can insert product logs"
ON public.product_logs
FOR INSERT
TO service_role
WITH CHECK (true);

-- Create policy to allow authenticated users to read logs
CREATE POLICY "Users can read product logs"
ON public.product_logs
FOR SELECT
TO authenticated
USING (true);

-- Grant necessary permissions
GRANT INSERT ON public.product_logs TO service_role;
GRANT SELECT ON public.product_logs TO authenticated;

-- Verify RLS is enabled
ALTER TABLE public.product_logs ENABLE ROW LEVEL SECURITY;

COMMENT ON POLICY "Service role can insert product logs" ON public.product_logs IS 
'Allows automated scripts and triggers using service_role key to insert product change logs';
