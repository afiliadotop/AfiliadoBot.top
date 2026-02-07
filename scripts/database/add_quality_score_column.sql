-- Migration: Add quality_score column to products table
-- Date: 2026-02-07
-- Purpose: Enable quality-based product filtering in analytics

-- Add quality_score column (0-100)
ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS quality_score INTEGER DEFAULT 0;

-- Add comment explaining the scoring system
COMMENT ON COLUMN public.products.quality_score IS 
'Quality score (0-100) calculated from: rating (30pts), sales (30pts), commission (25pts), price stability (15pts). Higher = better quality. Minimum import threshold: 60.';

-- Create index for fast sorting by quality
CREATE INDEX IF NOT EXISTS idx_products_quality_score 
ON public.products(quality_score DESC) 
WHERE is_active = TRUE;

-- Create index for analytics queries (quality + clicks)
CREATE INDEX IF NOT EXISTS idx_products_quality_analytics 
ON public.products(quality_score DESC, created_at DESC) 
WHERE is_active = TRUE;

-- Update existing products with NULL quality_score to 0
UPDATE public.products 
SET quality_score = 0 
WHERE quality_score IS NULL;

-- Verify migration
SELECT 
    COUNT(*) as total_products,
    COUNT(CASE WHEN quality_score IS NOT NULL THEN 1 END) as with_quality_score,
    AVG(quality_score) as avg_quality_score,
    MAX(quality_score) as max_quality_score
FROM public.products 
WHERE is_active = TRUE;
