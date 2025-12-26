export interface Product {
    id: string; // Changed from number to string for UUID support
    name: string;
    store: 'shopee' | 'aliexpress' | 'amazon' | 'magalu' | 'mercadolivre' | 'temu' | 'shein' | string;
    current_price: number;
    original_price?: number;
    discount_percentage?: number;
    category?: string;
    image_url?: string;
    affiliate_link?: string;
    rating?: number;
    review_count?: number;
    is_active?: boolean;
}

export interface DashboardStats {
    total_products: number;
    active_products: number;
    connected_stores: number;
    active_coupons: number;
    monthly_revenue?: number;
    telegram_sends: number;
}

export interface User {
    id: string | number;
    name: string;
    email: string;
    role: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User;
}

