-- Migration: Awin Products and Offers Tables
-- @database-architect

-- ============================================================
-- TABLE: awin_products
-- Produtos importados via Awin Product Feed (Google Format)
-- ============================================================

CREATE TABLE IF NOT EXISTS awin_products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Identificação Awin
    awin_product_id TEXT NOT NULL,
    advertiser_id INTEGER NOT NULL,
    advertiser_name TEXT,
    
    -- Dados do Produto
    title TEXT NOT NULL,
    description TEXT,
    link TEXT NOT NULL,
    image_url TEXT,
    additional_images JSONB DEFAULT '[]',
    
    -- Preço (ISO 4217)
    price NUMERIC(12, 2),
    sale_price NUMERIC(12, 2),
    currency TEXT DEFAULT 'BRL',
    availability TEXT DEFAULT 'in_stock',
    
    -- Classificação
    brand TEXT,
    category TEXT,
    product_type TEXT,
    google_product_category TEXT,
    
    -- Atributos de Produto
    condition TEXT DEFAULT 'new',
    gtin TEXT,
    mpn TEXT,
    color TEXT,
    size TEXT,
    gender TEXT,
    material TEXT,
    
    -- Link de Afiliado (gerado via LinkBuilder)
    affiliate_link TEXT,
    
    -- Controle
    is_active BOOLEAN DEFAULT TRUE,
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(awin_product_id, advertiser_id)
);

-- Indexes para performance
CREATE INDEX IF NOT EXISTS idx_awin_products_advertiser ON awin_products(advertiser_id);
CREATE INDEX IF NOT EXISTS idx_awin_products_active ON awin_products(is_active);
CREATE INDEX IF NOT EXISTS idx_awin_products_price ON awin_products(price);
CREATE INDEX IF NOT EXISTS idx_awin_products_brand ON awin_products(brand);
CREATE INDEX IF NOT EXISTS idx_awin_products_category ON awin_products(category);

-- ============================================================
-- TABLE: awin_offers
-- Promoções, cupons e deals dos anunciantes Awin
-- ============================================================

CREATE TABLE IF NOT EXISTS awin_offers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Identificação
    awin_offer_id TEXT NOT NULL UNIQUE,
    advertiser_id INTEGER NOT NULL,
    advertiser_name TEXT,
    
    -- Dados da Oferta
    title TEXT NOT NULL,
    description TEXT,
    promotion_type TEXT, -- voucher | deal | product
    code TEXT,           -- Código de cupom (se voucher)
    
    -- Valores (se deal)
    discount_value NUMERIC(10, 2),
    discount_type TEXT, -- percentage | fixed
    minimum_order NUMERIC(10, 2),
    
    -- Validade
    starts_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    
    -- URLs
    deeplink TEXT,
    tracking_link TEXT,
    
    -- Controle
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_awin_offers_advertiser ON awin_offers(advertiser_id);
CREATE INDEX IF NOT EXISTS idx_awin_offers_type ON awin_offers(promotion_type);
CREATE INDEX IF NOT EXISTS idx_awin_offers_expires ON awin_offers(expires_at);
CREATE INDEX IF NOT EXISTS idx_awin_offers_active ON awin_offers(is_active);

-- ============================================================
-- RLS POLICIES
-- ============================================================

ALTER TABLE awin_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE awin_offers ENABLE ROW LEVEL SECURITY;

-- Apenas admins podem gerenciar
CREATE POLICY "Somente admins gerenciam awin_products"
ON awin_products FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

-- Usuários autenticados podem ler
CREATE POLICY "Usuários autenticados leem awin_products"
ON awin_products FOR SELECT
USING (auth.role() = 'authenticated');

CREATE POLICY "Somente admins gerenciam awin_offers"
ON awin_offers FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Usuários autenticados leem awin_offers"
ON awin_offers FOR SELECT
USING (auth.role() = 'authenticated');

-- ============================================================
-- FUNCTION: update_updated_at trigger
-- ============================================================

CREATE OR REPLACE FUNCTION update_awin_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_awin_products_updated_at
BEFORE UPDATE ON awin_products
FOR EACH ROW EXECUTE FUNCTION update_awin_updated_at();

CREATE TRIGGER trg_awin_offers_updated_at
BEFORE UPDATE ON awin_offers
FOR EACH ROW EXECUTE FUNCTION update_awin_updated_at();
