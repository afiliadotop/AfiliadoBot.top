-- ===============================================
-- CORREÇÃO CRÍTICA DE SEGURANÇA
-- Data: 2026-01-22
-- ITIL Change: Emergency (Security Incident)
-- Severidade: P0 - CRITICAL
-- ===============================================

-- BACKUP RECOMENDADO ANTES DE EXECUTAR!

BEGIN;

-- ===============================================
-- 1. HABILITAR RLS NA TABELA SETTINGS
-- ===============================================
-- Fix: 0007_policy_exists_rls_disabled
-- Fix: 0013_rls_disabled_in_public

ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;

-- Verificar se políticas existem
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'settings' 
        AND policyname = 'Admin Access Settings'
    ) THEN
        RAISE NOTICE 'RLS habilitado para settings - Policy "Admin Access Settings" já existe';
    ELSE
        RAISE WARNING 'Policy "Admin Access Settings" não encontrada - pode precisar ser criada';
    END IF;
END $$;

-- ===============================================
-- 2. CORRIGIR SECURITY DEFINER VIEW
-- ===============================================
-- Fix: 0010_security_definer_view

-- Drop view antiga
DROP VIEW IF EXISTS public.shopee_products_summary;

-- Recriar com SECURITY INVOKER (permissões do usuário atual)
CREATE OR REPLACE VIEW public.shopee_products_summary
WITH (security_invoker = true)  -- PostgreSQL 15+
AS
SELECT 
    id,
    name,
    current_price,
    original_price,
    discount_percentage,
    commission_rate,
    affiliate_link,
    image_url,
    is_active,
    created_at,
    updated_at
FROM public.products
WHERE store = 'shopee' AND is_active = true;

COMMENT ON VIEW public.shopee_products_summary IS 
'View de produtos Shopee com SECURITY INVOKER (permissões do usuário atual)';

-- ===============================================
-- 3. CORRIGIR POLICIES - TELEGRAM_SETTINGS
-- ===============================================
-- Fix: 0015_rls_references_user_metadata (4 policies)

-- DROP policies inseguras que usam user_metadata
DROP POLICY IF EXISTS "Admin users can select" ON public.telegram_settings;
DROP POLICY IF EXISTS "Admin users can insert" ON public.telegram_settings;
DROP POLICY IF EXISTS "Admin users can update" ON public.telegram_settings;
DROP POLICY IF EXISTS "Admin users can delete" ON public.telegram_settings;

-- CRIAR policies seguras com app_metadata
CREATE POLICY "Admin users can select" ON public.telegram_settings
FOR SELECT
USING (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
);

CREATE POLICY "Admin users can insert" ON public.telegram_settings
FOR INSERT
WITH CHECK (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
);

CREATE POLICY "Admin users can update" ON public.telegram_settings
FOR UPDATE
USING (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
)
WITH CHECK (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
);

CREATE POLICY "Admin users can delete" ON public.telegram_settings
FOR DELETE
USING (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
);

-- ===============================================
-- 4. CORRIGIR POLICIES - PRODUCT_FEEDS
-- ===============================================
-- Fix: 0015_rls_references_user_metadata (2 policies)

-- DROP policies inseguras
DROP POLICY IF EXISTS "Admins can view product feeds" ON public.product_feeds;
DROP POLICY IF EXISTS "Admins can manage product feeds" ON public.product_feeds;

-- CRIAR policies seguras
CREATE POLICY "Admins can view product feeds" ON public.product_feeds
FOR SELECT
USING (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
);

CREATE POLICY "Admins can manage product feeds" ON public.product_feeds
FOR ALL
USING (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
)
WITH CHECK (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
);

-- ===============================================
-- 5. VERIFICAÇÕES FINAIS
-- ===============================================

-- Verificar RLS habilitado
DO $$
DECLARE
    v_rls_enabled boolean;
BEGIN
    SELECT relrowsecurity INTO v_rls_enabled
    FROM pg_class
    WHERE relname = 'settings' AND relnamespace = 'public'::regnamespace;
    
    IF v_rls_enabled THEN
        RAISE NOTICE '✅ RLS habilitado em public.settings';
    ELSE
        RAISE EXCEPTION '❌ ERRO: RLS não está habilitado em public.settings';
    END IF;
END $$;

-- Contar policies atualizadas
DO $$
DECLARE
    v_telegram_count integer;
    v_feeds_count integer;
BEGIN
    SELECT COUNT(*) INTO v_telegram_count
    FROM pg_policies
    WHERE tablename = 'telegram_settings';
    
    SELECT COUNT(*) INTO v_feeds_count
    FROM pg_policies
    WHERE tablename = 'product_feeds';
    
    RAISE NOTICE '✅ telegram_settings: % policies', v_telegram_count;
    RAISE NOTICE '✅ product_feeds: % policies', v_feeds_count;
END $$;

-- ===============================================
-- COMMIT OU ROLLBACK
-- ===============================================

-- Se tudo OK, COMMIT
-- Se algum erro, ROLLBACK automático
COMMIT;

-- ===============================================
-- PÓS-EXECUÇÃO MANUAL OBRIGATÓRIA
-- ===============================================

/* 
IMPORTANTE: Após executar este script, você DEVE:

1. Migrar usuários admin para app_metadata:
   - Ir em Supabase Dashboard > Authentication > Users
   - Para cada usuário admin, editar e adicionar em "User Metadata" (app section):
     {
       "role": "admin"
     }

2. Verificar Database Linter:
   - Ir em Supabase Dashboard > Database > Linter
   - Confirmar 0 erros de segurança

3. Testar acesso:
   - Login como admin → deve funcionar
   - Login como usuário normal → NÃO deve ter acesso

4. Documentar no Change Management:
   - RFC criado
   - Mudança aplicada
   - Validação completa
*/
