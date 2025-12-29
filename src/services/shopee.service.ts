import { api } from "./api";

// ==================== TYPES ====================

export interface ShopeeProduct {
    itemId: number;
    productName: string;
    priceMin: string;
    priceMax: string;
    imageUrl: string;
    sales: number;
    rating?: string;
    discountRate: number;
    shopName: string;
    offerLink: string;

    // Admin only - undefined for regular users
    commissionRate?: string;
    commissionAmount?: string;
    sellerCommissionRate?: string;
    shopeeCommissionRate?: string;
}

export interface ShopeeStats {
    totalProducts: number;
    avgCommission: number;
    topCommission: number;
    todayImports: number;
    lastSyncTime?: string;
}

export interface ShopeeSyncStatus {
    id: string;
    sync_type: string;
    products_imported: number;
    products_updated: number;
    errors: number;
    created_at: string;
    metadata?: Record<string, any>;
}

export interface ProductFilters {
    keyword?: string;
    sortBy?: 'commission' | 'sales' | 'price';
    limit?: number;
    // Advanced filters
    priceMin?: number;
    priceMax?: number;
    minRating?: number;
    minSales?: number;
    minDiscount?: number;
}

export interface PaginationInfo {
    page: number;
    limit: number;
    total: number;
    hasMore: boolean;
    totalPages: number;
}

export interface ProductsResponse {
    products: ShopeeProduct[];
    pagination: PaginationInfo;
    appliedFilters: Record<string, any>;
}

export interface FavoriteProduct extends ShopeeProduct {
    favoriteId: string;
    favoritedAt: string;
}

export interface FavoritesResponse {
    favorites: FavoriteProduct[];
    count: number;
}

export interface SearchRequest {
    keyword: string;
    sortType?: number;
    limit?: number;
}

export interface GenerateLinkRequest {
    url: string;
    subIds?: string[];
}

export interface ProductSearchResponse {
    products: ShopeeProduct[];
    count: number;
    hasMore: boolean;
}

// ==================== SERVICE ====================

export const shopeeService = {
    /**
     * Get Shopee products with pagination and filters
     * Admin users will see commission data, regular users won't
     */
    getProducts: async (
        filters: ProductFilters = {},
        page: number = 1,
        limit: number = 20
    ): Promise<ProductsResponse | null> => {
        const params = new URLSearchParams();

        // Pagination
        params.append('page', page.toString());
        params.append('limit', limit.toString());

        // Search & Sort
        if (filters.keyword) params.append('keyword', filters.keyword);
        if (filters.sortBy) params.append('sort_by', filters.sortBy);

        // Advanced Filters
        if (filters.priceMin !== undefined) params.append('price_min', filters.priceMin.toString());
        if (filters.priceMax !== undefined) params.append('price_max', filters.priceMax.toString());
        if (filters.minRating !== undefined) params.append('min_rating', filters.minRating.toString());
        if (filters.minSales !== undefined) params.append('min_sales', filters.minSales.toString());
        if (filters.minDiscount !== undefined) params.append('min_discount', filters.minDiscount.toString());

        return await api.get<ProductsResponse>(`/shopee/products?${params.toString()}`);
    },

    /**
     * Search products by keyword
     */
    searchProducts: async (request: SearchRequest): Promise<ProductSearchResponse | null> => {
        return await api.post<ProductSearchResponse>('/shopee/search', {
            keyword: request.keyword,
            sortType: request.sortType || 5,
            limit: request.limit || 20
        });
    },

    /**
     * Generate affiliate short link
     * User ID is automatically added to sub_ids for tracking
     */
    generateShortLink: async (request: GenerateLinkRequest): Promise<{ shortLink: string; originalUrl: string } | null> => {
        return await api.post('/shopee/generate-link', request);
    },

    /**
     * Get general Shopee offers
     */
    getOffers: async (keyword?: string, limit: number = 10): Promise<{ nodes: any[]; pageInfo: any } | null> => {
        const params = new URLSearchParams();
        if (keyword) params.append('keyword', keyword);
        params.append('limit', limit.toString());

        return await api.get(`/shopee/offers?${params.toString()}`);
    },

    // ==================== ADMIN ONLY ====================

    /**
     * Get Shopee statistics - ADMIN ONLY
     */
    getStats: async (): Promise<ShopeeStats | null> => {
        return await api.get<ShopeeStats>('/shopee/stats');
    },

    /**
     * Get last sync status - ADMIN ONLY
     */
    getSyncStatus: async (): Promise<ShopeeSyncStatus | null> => {
        return await api.get<ShopeeSyncStatus>('/shopee/sync-status');
    },

    /**
     * Get top commission products - ADMIN ONLY
     */
    getTopCommission: async (limit: number = 10): Promise<{ products: ShopeeProduct[]; count: number } | null> => {
        return await api.get(`/shopee/top-commission?limit=${limit}`);
    },

    /**
     * Get rate limit status - ADMIN ONLY
     */
    getRateLimitStatus: async (): Promise<{
        used: number;
        remaining: number;
        total: number;
        reset_in_seconds: number;
        percentage_used: number;
    } | null> => {
        return await api.get('/shopee/rate-limit-status');
    },

    // ==================== FAVORITES ====================

    /**
     * Add product to favorites
     */
    addFavorite: async (itemId: number): Promise<{ status: string; itemId: number } | null> => {
        return await api.post(`/shopee/favorites/${itemId}`, {});
    },

    /**
     * Remove product from favorites
     */
    removeFavorite: async (itemId: number): Promise<{ status: string; itemId: number } | null> => {
        return await api.delete(`/shopee/favorites/${itemId}`);
    },

    /**
     * Get user's favorites
     */
    getFavorites: async (): Promise<FavoritesResponse | null> => {
        return await api.get<FavoritesResponse>('/shopee/favorites');
    },

    /**
     * Check if product is favorited
     */
    checkFavorite: async (itemId: number): Promise<{ isFavorite: boolean; itemId: number } | null> => {
        return await api.get(`/shopee/favorites/check/${itemId}`);
    },

    /**
     * Envia um produto para o Telegram
     */
    sendProductToTelegram: async (itemId: number, productData: ShopeeProduct): Promise<{ success: boolean; message: string; product_name?: string } | null> => {
        return await api.post(`/shopee/products/${itemId}/send-to-telegram`, productData);
    }
};
