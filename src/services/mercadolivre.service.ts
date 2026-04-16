/**
 * Mercado Livre Service — Vercel Authenticated Proxy
 *
 * Problema raiz (confirmado na doc oficial ML):
 *   - ML bloqueia IPs de datacenter sem autenticação (403)
 *   - ML bloqueia CORS de origens externas (403)
 *   - Rewrite simples no Vercel não resolve: ainda recebe 403 sem Bearer token
 *
 * Solução:
 *   Vercel Serverless Function /api/ml-search que:
 *   1. Recebe a query do browser (same-origin, sem CORS)
 *   2. Adiciona Authorization: Bearer ML_ACCESS_TOKEN (env var no Vercel)
 *   3. Chama api.mercadolibre.com autenticado → 200 OK
 *
 * Referência doc ML: "Em toda chamada, enviar o access token em todas elas"
 */

const ML_PROXY_URL = '/api/ml-search';
const ML_AFFILIATE_TAG = 'TG-695d2ec34ff75f00019fb064-2307648221';

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

function buildAffiliateLink(itemId: string): string {
    const numericId = itemId.replace('MLB-', '').replace('MLB', '');
    return `https://produto.mercadolivre.com.br/MLB-${numericId}?matt_tool=82322591&matt_word=${ML_AFFILIATE_TAG}`;
}

function mapItem(item: any): MLProduct {
    const price = item.price ?? 0;
    const original = item.original_price;
    const discount = (original && original > price)
        ? Math.round(((original - price) / original) * 100)
        : 0;

    const image = (item.thumbnail ?? '').replace('-I.jpg', '-O.jpg');

    return {
        id: item.id,
        name: item.title,
        price,
        original_price: original ?? undefined,
        discount_percentage: discount,
        image_url: image,
        seller_name: item.seller?.nickname ?? 'N/A',
        condition: item.condition ?? 'new',
        shipping_free: item.shipping?.free_shipping ?? false,
        permalink: item.permalink ?? '',
        affiliate_link: buildAffiliateLink(item.id),
        sold_quantity: item.sold_quantity ?? undefined,
    };
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
    const offset = (page - 1) * limit;

    const params = new URLSearchParams({
        q: keyword,
        limit: String(limit),
        offset: String(offset),
    });

    const sortMap: Record<string, string> = {
        price_asc: 'price_asc',
        price_desc: 'price_desc',
        sales: 'sold_quantity',
    };
    if (sortMap[sort]) params.append('sort', sortMap[sort]);

    if (condition !== 'not_specified') {
        params.append('condition', condition);
    }

    // Chama Vercel Function (same-origin, sem CORS)
    // A Function adiciona o Bearer token para autenticar no ML
    const url = `${ML_PROXY_URL}?${params.toString()}`;
    const response = await fetch(url);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error((errorData as any).error || `ML API retornou ${response.status}`);
    }

    const data = await response.json();
    const products = (data.results ?? []).map(mapItem);
    const total = data.paging?.total ?? 0;

    return {
        products,
        count: products.length,
        total,
        page,
        has_more: offset + limit < total,
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
