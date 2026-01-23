-- ===============================================
-- PROMOVER USUÁRIOS ESPECÍFICOS PARA ADMIN
-- Data: 2026-01-22
-- ===============================================

BEGIN;

-- ===============================================
-- PROMOVER USUÁRIOS PARA ADMIN em app_metadata
-- ===============================================

-- Usuário 1: kenatocorretor@gmail.com (Paulo)
UPDATE auth.users
SET raw_app_meta_data = raw_app_meta_data || '{"role": "admin"}'::jsonb
WHERE email = 'kenatocorretor@gmail.com';

-- Usuário 2: teste@afiliado.top
UPDATE auth.users
SET raw_app_meta_data = raw_app_meta_data || '{"role": "admin"}'::jsonb
WHERE email = 'teste@afiliado.top';

-- Usuário 3: admin@afiliado.top (já deveria ter migrado, mas garantir)
UPDATE auth.users
SET raw_app_meta_data = 
    COALESCE(raw_app_meta_data, '{}'::jsonb) || 
    '{"role": "admin"}'::jsonb
WHERE email = 'admin@afiliado.top';

-- ===============================================
-- VERIFICAR ADMINS
-- ===============================================

SELECT 
    email,
    raw_app_meta_data->>'role' as role,
    CASE 
        WHEN raw_app_meta_data->>'role' = 'admin' THEN '✅ ADMIN'
        ELSE '❌ NÃO É ADMIN'
    END as status,
    created_at,
    last_sign_in_at
FROM auth.users
WHERE email IN (
    'admin@afiliado.top',
    'kenatocorretor@gmail.com', 
    'teste@afiliado.top'
)
ORDER BY email;

-- ===============================================
-- CONFIRMAR SEGURANÇA
-- ===============================================

DO $$
DECLARE
    v_admin_count integer;
BEGIN
    SELECT COUNT(*) INTO v_admin_count
    FROM auth.users
    WHERE raw_app_meta_data->>'role' = 'admin';
    
    RAISE NOTICE '✅ Total de admins: %', v_admin_count;
    
    -- Verificar se algum admin ainda tem role em user_metadata (INSEGURO)
    IF EXISTS (
        SELECT 1 FROM auth.users 
        WHERE raw_app_meta_data->>'role' = 'admin'
        AND raw_user_meta_data ? 'role'
    ) THEN
        RAISE WARNING '⚠️ Alguns admins ainda têm role em user_metadata! Execute migrate_role_to_app_metadata.sql';
    ELSE
        RAISE NOTICE '✅ Nenhum admin com role em user_metadata (seguro)';
    END IF;
END $$;

COMMIT;

-- ===============================================
-- PÓS-EXECUÇÃO
-- ===============================================

/*
Após executar este script:

1. Verificar que os 3 usuários são admins:
   - admin@afiliado.top
   - kenatocorretor@gmail.com
   - teste@afiliado.top

2. Testar login de cada um e verificar acesso a:
   - telegram_settings
   - product_feeds
   - settings

3. Confirmar que usuários normais NÃO têm acesso

4. Executar fix_security_vulnerabilities.sql se ainda não executou
   (para garantir que policies usam app_metadata)
*/
