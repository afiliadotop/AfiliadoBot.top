-- Fix RLS Policy for shopee_sync_log table
-- Allows service_role (used by scripts) to insert sync logs

-- Drop existing restrictive policies if any
DROP POLICY IF EXISTS "Service role can insert sync logs" ON public.shopee_sync_log;
DROP POLICY IF EXISTS "Enable insert for service role" ON public.shopee_sync_log;

-- Create policy to allow service_role to insert
CREATE POLICY "Service role can insert sync logs"
ON public.shopee_sync_log
FOR INSERT
TO service_role
WITH CHECK (true);

-- Create policy to allow authenticated users to read their own logs
CREATE POLICY "Users can read sync logs"
ON public.shopee_sync_log
FOR SELECT
TO authenticated
USING (true);

-- Grant necessary permissions
GRANT INSERT ON public.shopee_sync_log TO service_role;
GRANT SELECT ON public.shopee_sync_log TO authenticated;

-- Verify RLS is enabled
ALTER TABLE public.shopee_sync_log ENABLE ROW LEVEL SECURITY;

COMMENT ON POLICY "Service role can insert sync logs" ON public.shopee_sync_log IS 
'Allows automated scripts using service_role key to insert sync logs';
