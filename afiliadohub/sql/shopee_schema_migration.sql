-- Shopee Integration Database Migration
-- Extends existing schema for Shopee-specific data
-- Run in Supabase SQL Editor

-- 1. Add Shopee-specific columns to products table
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS shopee_product_id BIGINT,
ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS commission_amount DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS shopee_category VARCHAR(100),
ADD COLUMN IF NOT EXISTS sales_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS stock_available BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS shop_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS shop_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS review_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS rating DECIMAL(3,2);

-- 2. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_shopee_id ON products(shopee_product_id);
CREATE INDEX IF NOT EXISTS idx_products_commission_rate ON products(commission_rate DESC);
CREATE INDEX IF NOT EXISTS idx_products_sales ON products(sales_count DESC);
CREATE INDEX IF NOT EXISTS idx_products_shopee_category ON products(shopee_category);

-- 3. Create shopee_sync_log table
CREATE TABLE IF NOT EXISTS public.shopee_sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_type VARCHAR(50) NOT NULL,
    products_imported INT DEFAULT 0,
    products_updated INT DEFAULT 0,
    errors INT DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'running',
    error_messages TEXT[],
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_shopee_sync_log_started ON shopee_sync_log(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_shopee_sync_log_status ON shopee_sync_log(status);

-- 4. Add Shopee settings
INSERT INTO public.settings (key, value, description) VALUES
(
    'shopee_api',
    '{
        "app_id": "18353920154",
        "enabled": true,
        "auto_sync": true,
        "sync_interval_hours": 24,
        "min_commission_rate": 5.0,
        "last_sync": null
    }'::jsonb,
    'Shopee API Configuration and Settings'
)
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    updated_at = NOW();

-- 5. Function to get outdated Shopee products
CREATE OR REPLACE FUNCTION get_outdated_shopee_products(hours_old INT DEFAULT 24)
RETURNS SETOF products AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM products
    WHERE store = 'shopee'
    AND last_checked < NOW() - (hours_old || ' hours')::INTERVAL
    ORDER BY last_checked ASC
    LIMIT 100;
END;
$$ LANGUAGE plpgsql;

-- 6. Function to get top commission products
CREATE OR REPLACE FUNCTION get_top_commission_products(p_limit INT DEFAULT 10)
RETURNS SETOF products AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM products
    WHERE store = 'shopee'
    AND is_active = TRUE
    AND commission_rate > 0
    ORDER BY commission_rate DESC, sales_count DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 7. Function to log sync operation
CREATE OR REPLACE FUNCTION log_shopee_sync(
    p_sync_type VARCHAR,
    p_products_imported INT,
    p_products_updated INT,
    p_errors INT,
    p_error_messages TEXT[] DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    sync_id UUID;
BEGIN
    INSERT INTO shopee_sync_log (
        sync_type,
        products_imported,
        products_updated,
        errors,
        completed_at,
        status,
        error_messages,
        metadata
    ) VALUES (
        p_sync_type,
        p_products_imported,
        p_products_updated,
        p_errors,
        NOW(),
        CASE WHEN p_errors > 0 THEN 'completed_with_errors' ELSE 'completed' END,
        p_error_messages,
        p_metadata
    )
    RETURNING id INTO sync_id;
    
    -- Update last sync time in settings
    UPDATE settings
    SET value = jsonb_set(value, '{last_sync}', to_jsonb(NOW()))
    WHERE key = 'shopee_api';
    
    RETURN sync_id;
END;
$$ LANGUAGE plpgsql;

-- 8. Function to get Shopee statistics
CREATE OR REPLACE FUNCTION get_shopee_statistics()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    total_products INT;
    active_products INT;
    avg_commission DECIMAL(5,2);
    total_sales INT;
    last_sync TIMESTAMPTZ;
BEGIN
    -- Get stats
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE is_active = TRUE),
        AVG(commission_rate),
        SUM(sales_count)
    INTO total_products, active_products, avg_commission, total_sales
    FROM products
    WHERE store = 'shopee';
    
    -- Get last sync
    SELECT value->>'last_sync' INTO last_sync
    FROM settings
    WHERE key = 'shopee_api';
    
    -- Build result
    result := jsonb_build_object(
        'total_products', COALESCE(total_products, 0),
        'active_products', COALESCE(active_products, 0),
        'average_commission', COALESCE(avg_commission, 0),
        'total_sales', COALESCE(total_sales, 0),
        'last_sync', last_sync,
        'sync_enabled', (SELECT value->>'enabled' FROM settings WHERE key = 'shopee_api')::BOOLEAN
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 9. View for Shopee products summary
CREATE OR REPLACE VIEW shopee_products_summary AS
SELECT 
    COUNT(*) as total_products,
    COUNT(*) FILTER (WHERE is_active = TRUE) as active_products,
    COUNT(*) FILTER (WHERE discount_percentage > 0) as discounted_products,
    AVG(commission_rate) as avg_commission_rate,
    MAX(commission_rate) as max_commission_rate,
    SUM(sales_count) as total_sales,
    COUNT(DISTINCT shopee_category) as total_categories
FROM products
WHERE store = 'shopee';

-- 10. Grants (adjust as needed for your security setup)
-- These are examples, adjust based on your authentication setup
-- GRANT SELECT, INSERT, UPDATE ON products TO authenticated;
-- GRANT SELECT, INSERT ON shopee_sync_log TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_outdated_shopee_products TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_top_commission_products TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_shopee_statistics TO authenticated;

-- Comments for documentation
COMMENT ON COLUMN products.shopee_product_id IS 'ID único do produto na Shopee';
COMMENT ON COLUMN products.commission_rate IS 'Taxa de comissão em porcentagem (ex: 5.5 para 5.5%)';
COMMENT ON COLUMN products.commission_amount IS 'Valor da comissão em reais';
COMMENT ON COLUMN products.sales_count IS 'Número de vendas do produto';
COMMENT ON COLUMN products.shop_name IS 'Nome da loja vendedora';
COMMENT ON COLUMN products.shop_rating IS 'Avaliação da loja (0-5)';

COMMENT ON TABLE shopee_sync_log IS 'Log de sincronizações com a API da Shopee';
COMMENT ON FUNCTION get_outdated_shopee_products IS 'Retorna produtos da Shopee que precisam de atualização';
COMMENT ON FUNCTION get_top_commission_products IS 'Retorna produtos com maiores comissões';
COMMENT ON FUNCTION log_shopee_sync IS 'Registra resultado de uma sincronização';
COMMENT ON FUNCTION get_shopee_statistics IS 'Retorna estatísticas gerais dos produtos Shopee';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Shopee migration completed successfully!';
    RAISE NOTICE '📊 New columns added to products table';
    RAISE NOTICE '📋 shopee_sync_log table created';
    RAISE NOTICE '⚙️ Settings and functions configured';
END $$;
