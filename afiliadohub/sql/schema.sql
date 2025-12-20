-- FULL MIGRATION SCRIPT (Consolidated)
-- Run this in Supabase SQL Editor

-- 1. Tables
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.stores (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    base_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INT REFERENCES public.categories(id),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id INT REFERENCES public.stores(id),
    store VARCHAR(50),
    name TEXT NOT NULL,
    description TEXT,
    affiliate_link TEXT NOT NULL UNIQUE,
    original_link TEXT,
    current_price NUMERIC(10, 2) NOT NULL,
    original_price NUMERIC(10, 2),
    discount_percentage INT,
    category_id INT REFERENCES public.categories(id),
    category VARCHAR(100),
    image_url TEXT,
    coupon_code VARCHAR(50),
    coupon_expiry TIMESTAMPTZ,
    tags TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    last_checked TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    search_vector TSVECTOR
);

CREATE TABLE IF NOT EXISTS public.product_stats (
    product_id UUID PRIMARY KEY REFERENCES public.products(id) ON DELETE CASCADE,
    view_count BIGINT DEFAULT 0,
    click_count BIGINT DEFAULT 0,
    telegram_send_count BIGINT DEFAULT 0,
    last_sent TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS public.product_logs (
    id SERIAL PRIMARY KEY,
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE,
    old_price NUMERIC(10, 2),
    new_price NUMERIC(10, 2),
    change_type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.settings (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.import_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name TEXT,
    store VARCHAR(50),
    total_rows INT,
    imported INT,
    errors INT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Indexes
CREATE INDEX IF NOT EXISTS idx_products_store ON public.products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_active ON public.products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_price ON public.products(current_price);
CREATE INDEX IF NOT EXISTS idx_products_created ON public.products(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_search ON public.products USING GIN(search_vector);

CREATE OR REPLACE FUNCTION products_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('portuguese', COALESCE(NEW.name, '')), 'A') ||
    setweight(to_tsvector('portuguese', COALESCE(NEW.description, '')), 'B') ||
    setweight(to_tsvector('portuguese', COALESCE(NEW.category, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tsvectorupdate ON public.products;
CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
ON public.products FOR EACH ROW EXECUTE PROCEDURE products_search_vector_update();

-- 3. Functions (RPC)
CREATE OR REPLACE FUNCTION increment_stat(p_product_id UUID, p_field TEXT, p_increment INT DEFAULT 1)
RETURNS VOID AS $$
BEGIN
    INSERT INTO public.product_stats (product_id, view_count, click_count, telegram_send_count, last_sent)
    VALUES (p_product_id, 
            CASE WHEN p_field = 'view_count' THEN p_increment ELSE 0 END,
            CASE WHEN p_field = 'click_count' THEN p_increment ELSE 0 END,
            CASE WHEN p_field = 'telegram_send_count' THEN p_increment ELSE 0 END,
            NOW())
    ON CONFLICT (product_id) DO UPDATE SET
        view_count = public.product_stats.view_count + CASE WHEN p_field = 'view_count' THEN p_increment ELSE 0 END,
        click_count = public.product_stats.click_count + CASE WHEN p_field = 'click_count' THEN p_increment ELSE 0 END,
        telegram_send_count = public.product_stats.telegram_send_count + CASE WHEN p_field = 'telegram_send_count' THEN p_increment ELSE 0 END,
        last_sent = CASE WHEN p_field = 'telegram_send_count' THEN NOW() ELSE public.product_stats.last_sent END;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_random_product(min_discount INT DEFAULT 0)
RETURNS SETOF products AS $$
BEGIN
  RETURN QUERY
  SELECT * FROM products
  WHERE is_active = TRUE
  AND (discount_percentage >= min_discount OR min_discount = 0)
  ORDER BY random()
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_table_counts()
RETURNS JSONB AS $$
DECLARE
    prod_count INT;
    stat_count INT;
BEGIN
    SELECT count(*) INTO prod_count FROM products;
    SELECT sum(telegram_send_count) INTO stat_count FROM product_stats;
    
    RETURN jsonb_build_object(
        'products', prod_count,
        'total_sends', COALESCE(stat_count, 0)
    );
END;
$$ LANGUAGE plpgsql;

-- 4. Initial Data
INSERT INTO public.stores (name, display_name, base_url) VALUES
('shopee', 'Shopee', 'https://shopee.com.br'),
('aliexpress', 'AliExpress', 'https://aliexpress.com'),
('amazon', 'Amazon', 'https://amazon.com.br'),
('magalu', 'Magazine Luiza', 'https://magazineluiza.com.br'),
('mercadolivre', 'Mercado Livre', 'https://mercadolivre.com.br'),
('shein', 'Shein', 'https://shein.com'),
('temu', 'Temu', 'https://temu.com')
ON CONFLICT (name) DO NOTHING;

INSERT INTO public.settings (key, value, description) VALUES
('telegram_config', '{"send_interval": "1 hour", "min_discount": 20}'::jsonb, 'Configuração do Bot'),
('system_config', '{"currency": "BRL", "tax_rate": 0}'::jsonb, 'Configurações Gerais')
ON CONFLICT (key) DO NOTHING;
