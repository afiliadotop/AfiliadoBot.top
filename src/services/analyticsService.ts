/**
 * Analytics Service
 * Client-side API service for analytics endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface PerformanceOverview {
    total_products: number;
    total_clicks: number;
    avg_ctr: number;
    avg_quality_score: number;
    best_store: string;
    period_days: number;
    generated_at: string;
}

export interface TopProduct {
    id: number;
    name: string;
    store: string;
    image_url: string;
    affiliate_link: string;
    current_price: number;
    discount_percentage: number;
    quality_score: number;
    click_count: number;
    telegram_send_count: number;
    ctr: number;
}

export interface StorePerformance {
    store: string;
    product_count: number;
    total_clicks: number;
    total_telegram_sends: number;
    avg_clicks_per_product: number;
    ctr: number;
}

export interface TrendData {
    date: string;
    clicks: number;
}

/**
 * Fetch performance overview
 */
export async function getPerformanceOverview(days: number = 30): Promise<PerformanceOverview> {
    const response = await fetch(`${API_BASE_URL}/analytics/overview?days=${days}`);

    if (!response.ok) {
        throw new Error('Failed to fetch performance overview');
    }

    return response.json();
}

/**
 * Fetch top products by metric
 */
export async function getTopProducts(
    limit: number = 10,
    metric: 'clicks' | 'telegram_sends' | 'quality_score' = 'clicks',
    days?: number
): Promise<{ products: TopProduct[]; count: number; metric: string }> {
    let url = `${API_BASE_URL}/analytics/top-products?limit=${limit}&metric=${metric}`;

    if (days) {
        url += `&days=${days}`;
    }

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error('Failed to fetch top products');
    }

    return response.json();
}

/**
 * Fetch store comparison
 */
export async function getStoreComparison(): Promise<{ stores: StorePerformance[]; count: number }> {
    const response = await fetch(`${API_BASE_URL}/analytics/stores`);

    if (!response.ok) {
        throw new Error('Failed to fetch store comparison');
    }

    return response.json();
}

/**
 * Fetch trends (click data over time)
 */
export async function getTrends(days: number = 30): Promise<{ trends: TrendData[]; count: number; period_days: number }> {
    const response = await fetch(`${API_BASE_URL}/analytics/trends?days=${days}`);

    if (!response.ok) {
        throw new Error('Failed to fetch trends');
    }

    return response.json();
}

/**
 * Health check
 */
export async function checkAnalyticsHealth(): Promise<{ status: string; service: string; version: string }> {
    const response = await fetch(`${API_BASE_URL}/analytics/health`);

    if (!response.ok) {
        throw new Error('Analytics service is down');
    }

    return response.json();
}
