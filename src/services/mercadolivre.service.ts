/**
 * Mercado Livre Service — Backend Proxy
 *
 * Arquitetura:
 *   Antes: Frontend → ML API diretamente (bloqueado por CORS/403 do ML)
 *   Agora:  Frontend → nosso backend (/api/mercadolivre/search) → ML API
 *
 * O ML bloqueia CORS de origens externas (Origin != *.mercadolivre.com.br).
 * O backend usa client_credentials token para autenticar e resolver o 403.
 */

const getBaseUrl = (): string => {
    const url = import.meta.env.VITE_API_URL || '/api';
    if (url.startsWith('http') && !url.endsWith('/api') && !url.includes('/api/')) {
        return url.endsWith('/') ? `${url}api` : `${url}/api`;
    }
    return url;
};

const BASE_URL = getBaseUrl();

const getAuthHeaders = (): HeadersInit => {
    const token = localStorage.getItem('afiliadobot_token');
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
    };
};

export interface MLProduct {
    id: string;
    name: string;
    price: number;
    original_price?: number;
    discount_percentage: number;
    image_url: string;
    seller_name: string;
    condition: 'new' | 'used' | 'not_specified';
    shipping_free: boolean;
    permalink: string;
    affiliate_link: string;
    sold_quantity?: number;
}

export interface MLSearchResult {
    products: MLProduct[];
    count: number;
    total: number;
    page: number;
    has_more: boolean;
}

export async function searchMLProducts(
    keyword: string,
    options: {
        sort?: 'relevance' | 'price_asc' | 'price_desc' | 'sales';
        condition?: 'new' | 'used' | 'not_specified';
        page?: number;
        limit?: number;
    } = {}
): Promise<MLSearchResult> {
    const { sort = 'relevance', condition = 'new', page = 1, limit = 20 } = options;

    const params = new URLSearchParams({
        keyword,
        limit: String(limit),
        page: String(page),
        sort,
        condition,
    });

    const response = await fetch(`${BASE_URL}/mercadolivre/search?${params.toString()}`, {
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const msg = (errorData as any).detail || `ML API retornou ${response.status}`;
        throw new Error(msg);
    }

    const data = await response.json();

    return {
        products: data.products ?? [],
        count: data.count ?? 0,
        total: data.total ?? 0,
        page: data.page ?? page,
        has_more: data.has_more ?? false,
    };
}

export async function getTrendingMLProducts(limit = 20): Promise<MLProduct[]> {
    try {
        const result = await searchMLProducts('ofertas do dia', {
            sort: 'sales',
            condition: 'new',
            limit,
        });
        return result.products;
    } catch {
        return [];
    }
}
