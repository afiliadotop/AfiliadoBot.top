-- Habilita extensão de UUID se não existir
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Tabelas Auxiliares (Lojas e Categorias)
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

-- 2. Tabela Principal de Produtos
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id INT REFERENCES public.stores(id),
    store VARCHAR(50), -- Mantido para compatibilidade legado
    name TEXT NOT NULL,
    description TEXT,
    affiliate_link TEXT NOT NULL UNIQUE,
    original_link TEXT,
    current_price NUMERIC(10, 2) NOT NULL,
    original_price NUMERIC(10, 2),
    discount_percentage INT,
    category_id INT REFERENCES public.categories(id),
    category VARCHAR(100), -- Mantido para compatibilidade legado
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

-- 3. Tabelas de Métricas e Logs
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

-- 4. Tabelas de Sistema
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
