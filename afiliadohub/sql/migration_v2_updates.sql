-- Função RPC para incremento atômico (Usada pelo Bot)
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

-- Função RPC para buscar produto aleatório (Usada pelo Bot e Cron)
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

-- Função RPC para Dashboard (Counts rápidos)
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
