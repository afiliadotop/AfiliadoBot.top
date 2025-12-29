-- User Preferences Migration
-- Run this in Supabase SQL Editor to add user preference tracking

-- 1. Create user_preferences table
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT NOT NULL UNIQUE,
    telegram_username VARCHAR(255),
    telegram_first_name VARCHAR(255),
    preferred_stores TEXT[],
    preferred_categories TEXT[],
    min_discount INT DEFAULT 0,
    max_price NUMERIC(10, 2),
    notification_enabled BOOLEAN DEFAULT TRUE,
    language VARCHAR(10) DEFAULT 'pt-BR',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create indexes
CREATE INDEX IF NOT EXISTS idx_user_prefs_telegram ON public.user_preferences(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_user_prefs_stores ON public.user_preferences USING GIN(preferred_stores);
CREATE INDEX IF NOT EXISTS idx_user_prefs_categories ON public.user_preferences USING GIN(preferred_categories);

-- 3. Create trigger to update updated_at
CREATE OR REPLACE FUNCTION update_user_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS user_preferences_updated_at ON public.user_preferences;
CREATE TRIGGER user_preferences_updated_at
    BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_user_preferences_updated_at();

-- 4. Function to get recommended products based on user preferences
CREATE OR REPLACE FUNCTION get_recommended_products(
    p_telegram_user_id BIGINT,
    p_limit INT DEFAULT 5
) RETURNS SETOF products AS $$
BEGIN
    RETURN QUERY
    SELECT p.* FROM products p
    LEFT JOIN user_preferences up ON up.telegram_user_id = p_telegram_user_id
    WHERE p.is_active = TRUE
    AND (
        up.id IS NULL OR  -- User has no preferences, return all
        (
            (up.preferred_stores IS NULL OR array_length(up.preferred_stores, 1) IS NULL OR p.store = ANY(up.preferred_stores)) AND
            (up.preferred_categories IS NULL OR array_length(up.preferred_categories, 1) IS NULL OR p.category = ANY(up.preferred_categories)) AND
            (up.min_discount IS NULL OR up.min_discount = 0 OR p.discount_percentage >= up.min_discount) AND
            (up.max_price IS NULL OR p.current_price <= up.max_price)
        )
    )
    ORDER BY 
        CASE WHEN p.discount_percentage IS NOT NULL THEN p.discount_percentage ELSE 0 END DESC,
        p.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 5. Function to get user preference summary
CREATE OR REPLACE FUNCTION get_user_preference_summary(p_telegram_user_id BIGINT)
RETURNS JSONB AS $$
DECLARE
    pref_record RECORD;
    result JSONB;
BEGIN
    SELECT * INTO pref_record FROM user_preferences WHERE telegram_user_id = p_telegram_user_id;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object(
            'has_preferences', false,
            'message', 'No preferences set'
        );
    END IF;
    
    result := jsonb_build_object(
        'has_preferences', true,
        'telegram_user_id', pref_record.telegram_user_id,
        'telegram_username', pref_record.telegram_username,
        'preferred_stores', COALESCE(pref_record.preferred_stores, ARRAY[]::TEXT[]),
        'preferred_categories', COALESCE(pref_record.preferred_categories, ARRAY[]::TEXT[]),
        'min_discount', COALESCE(pref_record.min_discount, 0),
        'max_price', pref_record.max_price,
        'notification_enabled', pref_record.notification_enabled,
        'created_at', pref_record.created_at,
        'updated_at', pref_record.updated_at
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 6. Function to upsert user preferences
CREATE OR REPLACE FUNCTION upsert_user_preference(
    p_telegram_user_id BIGINT,
    p_telegram_username VARCHAR DEFAULT NULL,
    p_telegram_first_name VARCHAR DEFAULT NULL,
    p_preferred_stores TEXT[] DEFAULT NULL,
    p_preferred_categories TEXT[] DEFAULT NULL,
    p_min_discount INT DEFAULT NULL,
    p_max_price NUMERIC DEFAULT NULL,
    p_notification_enabled BOOLEAN DEFAULT NULL
) RETURNS user_preferences AS $$
DECLARE
    result user_preferences;
BEGIN
    INSERT INTO user_preferences (
        telegram_user_id,
        telegram_username,
        telegram_first_name,
        preferred_stores,
        preferred_categories,
        min_discount,
        max_price,
        notification_enabled
    ) VALUES (
        p_telegram_user_id,
        p_telegram_username,
        p_telegram_first_name,
        p_preferred_stores,
        p_preferred_categories,
        COALESCE(p_min_discount, 0),
        p_max_price,
        COALESCE(p_notification_enabled, TRUE)
    )
    ON CONFLICT (telegram_user_id) DO UPDATE SET
        telegram_username = COALESCE(EXCLUDED.telegram_username, user_preferences.telegram_username),
        telegram_first_name = COALESCE(EXCLUDED.telegram_first_name, user_preferences.telegram_first_name),
        preferred_stores = COALESCE(EXCLUDED.preferred_stores, user_preferences.preferred_stores),
        preferred_categories = COALESCE(EXCLUDED.preferred_categories, user_preferences.preferred_categories),
        min_discount = COALESCE(EXCLUDED.min_discount, user_preferences.min_discount),
        max_price = COALESCE(EXCLUDED.max_price, user_preferences.max_price),
        notification_enabled = COALESCE(EXCLUDED.notification_enabled, user_preferences.notification_enabled),
        updated_at = NOW()
    RETURNING * INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 7. Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON public.user_preferences TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_recommended_products TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_user_preference_summary TO authenticated;
-- GRANT EXECUTE ON FUNCTION upsert_user_preference TO authenticated;

COMMENT ON TABLE public.user_preferences IS 'Stores user preferences for personalized product recommendations';
COMMENT ON FUNCTION get_recommended_products IS 'Returns products matching user preferences';
COMMENT ON FUNCTION get_user_preference_summary IS 'Returns JSON summary of user preferences';
COMMENT ON FUNCTION upsert_user_preference IS 'Creates or updates user preferences';
