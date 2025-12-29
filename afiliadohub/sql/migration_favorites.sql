-- ==========================================
-- Shopee Favorites System Migration
-- ==========================================

-- Create user_favorites table
CREATE TABLE IF NOT EXISTS public.user_favorites (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  item_id BIGINT NOT NULL,
  product_data JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, item_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id 
  ON public.user_favorites(user_id);

CREATE INDEX IF NOT EXISTS idx_user_favorites_item_id 
  ON public.user_favorites(item_id);

CREATE INDEX IF NOT EXISTS idx_user_favorites_created_at 
  ON public.user_favorites(created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.user_favorites ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can view own favorites" ON public.user_favorites;
DROP POLICY IF EXISTS "Users can insert own favorites" ON public.user_favorites;
DROP POLICY IF EXISTS "Users can delete own favorites" ON public.user_favorites;

-- RLS Policy: Users can only view their own favorites
CREATE POLICY "Users can view own favorites"
  ON public.user_favorites FOR SELECT
  USING (auth.uid() = user_id);

-- RLS Policy: Users can only insert their own favorites
CREATE POLICY "Users can insert own favorites"
  ON public.user_favorites FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can only delete their own favorites
CREATE POLICY "Users can delete own favorites"
  ON public.user_favorites FOR DELETE
  USING (auth.uid() = user_id);

-- Create trigger for updated_at (if update_updated_at_column function exists)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column'
  ) THEN
    DROP TRIGGER IF EXISTS update_user_favorites_updated_at ON public.user_favorites;
    
    CREATE TRIGGER update_user_favorites_updated_at
      BEFORE UPDATE ON public.user_favorites
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  END IF;
END $$;

-- Grant permissions
GRANT SELECT, INSERT, DELETE ON public.user_favorites TO authenticated;
GRANT USAGE ON SEQUENCE user_favorites_id_seq TO authenticated;

-- Add comment
COMMENT ON TABLE public.user_favorites IS 'Stores user favorite Shopee products with cached product data';
