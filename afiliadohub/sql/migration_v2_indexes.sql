-- Índices para buscas rápidas no Dashboard
CREATE INDEX IF NOT EXISTS idx_products_store ON public.products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_active ON public.products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_price ON public.products(current_price);
CREATE INDEX IF NOT EXISTS idx_products_created ON public.products(created_at DESC);

-- Índice de Busca Full-Text (Essencial para o comando /buscar do Telegram)
CREATE INDEX IF NOT EXISTS idx_products_search ON public.products USING GIN(search_vector);

-- Trigger para atualizar o vetor de busca automaticamente
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
