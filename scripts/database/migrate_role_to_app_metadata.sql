-- ===============================================
-- MIGRAÇÃO DE SEGURANÇA: user_metadata → app_metadata
-- Data: 2026-01-22
-- CRÍTICO: Mover role de user_metadata para app_metadata
-- ===============================================

-- PROBLEMA ATUAL:
-- role está em raw_user_meta_data (editável pelo usuário!)
-- Usuário pode fazer: supabase.auth.updateUser({data: {role: 'admin'}})

-- SOLUÇÃO:
-- Mover role para raw_app_meta_data (somente admin backend pode editar)

BEGIN;

-- ===============================================
-- 1. MIGRAR TODOS OS USUÁRIOS COM ROLE EM user_metadata
-- ===============================================

-- Atualizar usuários que têm role em user_metadata
UPDATE auth.users
SET raw_app_meta_data = 
    COALESCE(raw_app_meta_data, '{}'::jsonb) || 
    jsonb_build_object('role', raw_user_meta_data->>'role')
WHERE raw_user_meta_data ? 'role'
  AND (raw_user_meta_data->>'role') IS NOT NULL;

-- Remover role de user_metadata (agora que está em app_metadata)
UPDATE auth.users
SET raw_user_meta_data = raw_user_meta_data - 'role'
WHERE raw_user_meta_data ? 'role';

-- ===============================================
-- 2. VERIFICAÇÃO
-- ===============================================

-- Ver usuários admin migrados
SELECT 
    id,
    email,
    raw_app_meta_data->>'role' as app_role,
    raw_user_meta_data->>'role' as user_role,
    CASE 
        WHEN raw_app_meta_data->>'role' = 'admin' THEN '✅ MIGRADO'
        ELSE '❌ NÃO É ADMIN'
    END as status
FROM auth.users
WHERE raw_app_meta_data->>'role' = 'admin'
   OR raw_user_meta_data->>'role' = 'admin';

-- ===============================================
-- 3. CONFIRMAR SEGURANÇA
-- ===============================================

DO $$
DECLARE
    v_insecure_count integer;
    v_secure_count integer;
BEGIN
    -- Contar usuários COM role em user_metadata (INSEGURO)
    SELECT COUNT(*) INTO v_insecure_count
    FROM auth.users
    WHERE raw_user_meta_data ? 'role';
    
    -- Contar usuários COM role em app_metadata (SEGURO)
    SELECT COUNT(*) INTO v_secure_count
    FROM auth.users
    WHERE raw_app_meta_data ? 'role';
    
    IF v_insecure_count > 0 THEN
        RAISE WARNING '❌ ATENÇÃO: % usuários ainda têm role em user_metadata (INSEGURO)', v_insecure_count;
    ELSE
        RAISE NOTICE '✅ Nenhum usuário com role em user_metadata';
    END IF;
    
    IF v_secure_count > 0 THEN
        RAISE NOTICE '✅ % usuários com role em app_metadata (SEGURO)', v_secure_count;
    END IF;
END $$;

COMMIT;

-- ===============================================
-- PÓS-MIGRAÇÃO
-- ===============================================

/*
IMPORTANTE: Após executar este script:

1. Verificar que policies RLS já usam app_metadata:
   SELECT * FROM pg_policies 
   WHERE definition LIKE '%user_metadata%';
   
   Se alguma policy ainda usa user_metadata, execute:
   scripts/database/fix_security_vulnerabilities.sql

2. Testar login:
   - Login como admin → deve funcionar
   - Tentar editar user_metadata → role NÃO deve mudar

3. Documentar mudança no Change Management
*/
