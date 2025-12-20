-- Popula Lojas Suportadas
INSERT INTO public.stores (name, display_name, base_url) VALUES
('shopee', 'Shopee', 'https://shopee.com.br'),
('aliexpress', 'AliExpress', 'https://aliexpress.com'),
('amazon', 'Amazon', 'https://amazon.com.br'),
('magalu', 'Magazine Luiza', 'https://magazineluiza.com.br'),
('mercadolivre', 'Mercado Livre', 'https://mercadolivre.com.br'),
('shein', 'Shein', 'https://shein.com'),
('temu', 'Temu', 'https://temu.com')
ON CONFLICT (name) DO NOTHING;

-- Configuração Padrão
INSERT INTO public.settings (key, value, description) VALUES
('telegram_config', '{"send_interval": "1 hour", "min_discount": 20}'::jsonb, 'Configuração do Bot'),
('system_config', '{"currency": "BRL", "tax_rate": 0}'::jsonb, 'Configurações Gerais')
ON CONFLICT (key) DO NOTHING;
