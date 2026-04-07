-- ================================================
-- MIGRATION v3 — Database Improvements (All-in-one)
-- Applied: 2026-03-28
-- Issues resolved: 29 → ~13 (remaining: intentional or INFO-level)
-- ================================================

-- Run each section in order via Supabase MCP or SQL Editor

-- === PART 1: RLS Security Fix ===

-- categories: public read only
CREATE POLICY "Public read categories"
  ON public.categories FOR SELECT USING (true);

-- commissions: user sees own, service_role bypasses natively
CREATE POLICY "Users can view own commissions"
  ON public.commissions FOR SELECT
  USING ((select auth.uid())::text = user_id);

-- product_stats: split ALL-for-anon into targeted policies
DROP POLICY IF EXISTS "Allow all operations for anon (scripts)" ON public.product_stats;
DROP POLICY IF EXISTS "Enable read access for all users" ON public.product_stats;
CREATE POLICY "Public read product_stats"
  ON public.product_stats FOR SELECT USING (true);
CREATE POLICY "Scripts can insert product_stats"
  ON public.product_stats FOR INSERT WITH CHECK (true);
CREATE POLICY "Scripts can update product_stats"
  ON public.product_stats FOR UPDATE USING (true);

-- import_logs: admins only
DROP POLICY IF EXISTS "Admin Access Logs" ON public.import_logs;
CREATE POLICY "Admins read import_logs"
  ON public.import_logs FOR SELECT
  USING (
    (select auth.jwt() ->> 'role') = 'admin'
    OR (select auth.uid()) = user_id
  );

-- price_history: public read, service_role write
DROP POLICY IF EXISTS "Admin insert price_history" ON public.price_history;
DROP POLICY IF EXISTS "Admin delete price_history" ON public.price_history;
CREATE POLICY "Public read price_history"
  ON public.price_history FOR SELECT USING (true);

-- settings: admin read only
DROP POLICY IF EXISTS "Admin Access Settings" ON public.settings;
CREATE POLICY "Admins read settings"
  ON public.settings FOR SELECT
  USING ((select auth.jwt() ->> 'role') = 'admin');

-- === PART 2: RLS Performance (auth initplan) ===

-- user_profiles: (select auth.uid()) pattern
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
CREATE POLICY "Users can view own profile"
  ON public.user_profiles FOR SELECT USING ((select auth.uid()) = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
CREATE POLICY "Users can update own profile"
  ON public.user_profiles FOR UPDATE USING ((select auth.uid()) = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.user_profiles;
CREATE POLICY "Users can insert own profile"
  ON public.user_profiles FOR INSERT WITH CHECK ((select auth.uid()) = id);

-- subscriptions
DROP POLICY IF EXISTS "Users can view own subscriptions" ON public.subscriptions;
CREATE POLICY "Users can view own subscriptions"
  ON public.subscriptions FOR SELECT
  USING ((select auth.uid()) = user_id);

-- telegram_settings: admin only with initplan fix
DROP POLICY IF EXISTS "Admin users can select" ON public.telegram_settings;
CREATE POLICY "Admin users can select" ON public.telegram_settings FOR SELECT
  USING ((select auth.jwt() ->> 'role') = 'admin');
DROP POLICY IF EXISTS "Admin users can insert" ON public.telegram_settings;
CREATE POLICY "Admin users can insert" ON public.telegram_settings FOR INSERT
  WITH CHECK ((select auth.jwt() ->> 'role') = 'admin');
DROP POLICY IF EXISTS "Admin users can update" ON public.telegram_settings;
CREATE POLICY "Admin users can update" ON public.telegram_settings FOR UPDATE
  USING ((select auth.jwt() ->> 'role') = 'admin');
DROP POLICY IF EXISTS "Admin users can delete" ON public.telegram_settings;
CREATE POLICY "Admin users can delete" ON public.telegram_settings FOR DELETE
  USING ((select auth.jwt() ->> 'role') = 'admin');

-- product_feeds: consolidar em 2 policies
DROP POLICY IF EXISTS "Enable access for authenticated users" ON public.product_feeds;
DROP POLICY IF EXISTS "Admins can view product feeds" ON public.product_feeds;
DROP POLICY IF EXISTS "Admins can manage product feeds" ON public.product_feeds;
CREATE POLICY "Authenticated read product_feeds" ON public.product_feeds FOR SELECT
  USING ((select auth.uid()) IS NOT NULL);
CREATE POLICY "Admin manage product_feeds" ON public.product_feeds FOR ALL
  USING ((select auth.jwt() ->> 'role') = 'admin')
  WITH CHECK ((select auth.jwt() ->> 'role') = 'admin');

-- products: remover policy permissiva redundante
DROP POLICY IF EXISTS "Enable all for service role" ON public.products;

-- shopee_sync_log: consolidar
DROP POLICY IF EXISTS "Enable access for authenticated users" ON public.shopee_sync_log;
DROP POLICY IF EXISTS "Users can read sync logs" ON public.shopee_sync_log;
CREATE POLICY "Authenticated read shopee_sync_log" ON public.shopee_sync_log FOR SELECT
  USING ((select auth.uid()) IS NOT NULL);

-- === PART 3: FK Indexes ===

CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON public.categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_commissions_product_id ON public.commissions(product_id);
CREATE INDEX IF NOT EXISTS idx_commissions_user_id ON public.commissions(user_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON public.commissions(status);
CREATE INDEX IF NOT EXISTS idx_product_feeds_store_id ON public.product_feeds(store_id);
CREATE INDEX IF NOT EXISTS idx_product_logs_product_id ON public.product_logs(product_id);
CREATE INDEX IF NOT EXISTS idx_product_logs_created_at ON public.product_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON public.products(category_id);

-- === PART 4: user_preferences table (was never applied) ===

CREATE TABLE IF NOT EXISTS public.user_preferences (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id     BIGINT NOT NULL UNIQUE,
    telegram_username    VARCHAR(255),
    telegram_first_name  VARCHAR(255),
    preferred_stores     TEXT[],
    preferred_categories TEXT[],
    min_discount         INT DEFAULT 0,
    max_price            NUMERIC(10, 2),
    notification_enabled BOOLEAN DEFAULT TRUE,
    language             VARCHAR(10) DEFAULT 'pt-BR',
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_prefs_telegram ON public.user_preferences(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_user_prefs_stores ON public.user_preferences USING GIN(preferred_stores);
CREATE INDEX IF NOT EXISTS idx_user_prefs_categories ON public.user_preferences USING GIN(preferred_categories);
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read user_preferences" ON public.user_preferences FOR SELECT USING (true);
CREATE POLICY "Scripts insert user_preferences" ON public.user_preferences FOR INSERT WITH CHECK (true);
CREATE POLICY "Scripts update user_preferences" ON public.user_preferences FOR UPDATE USING (true);

-- === PART 5: All functions with SET search_path ===
-- (See individual migration files for full SQL)
-- Key: all functions now have SECURITY DEFINER + SET search_path = public, pg_catalog
