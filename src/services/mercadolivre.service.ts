/**
 * Mercado Livre Public API Service
 * Chama a API pública do ML diretamente do browser (sem backend)
 * ML bloqueia IPs de servidores cloud, mas permite browsers via CORS
 */

const ML_API_URL = 'https://api.mercadolibre.com';

// Headers que o browser envia automaticamente — API pública ML não requer auth
const getHeaders = () => ({
    'Accept': 'application/json',
    'Accept-Language': 'pt-BR,pt;q=0.9',
});

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

const ML_AFFILIATE_TAG = 'TG-695d2ec34ff75f00019fb064-2307648221';

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

    // Imagem em alta resolução
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

    // Mapeamento de sort para valores aceitos pela ML API
    const sortMap: Record<string, string> = {
        price_asc: 'price_asc',
        price_desc: 'price_desc',
        sales: 'sold_quantity',
    };
    if (sortMap[sort]) params.append('sort', sortMap[sort]);

    // Condition (só adiciona se não for "todos")
    if (condition !== 'not_specified') {
        params.append('condition', condition);
    }

    const url = `${ML_API_URL}/sites/MLB/search?${params.toString()}`;

    const response = await fetch(url, {
        headers: getHeaders(),
        mode: 'cors',
    });

    if (!response.ok) {
        throw new Error(`ML API retornou ${response.status}`);
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
    const params = new URLSearchParams({
        limit: String(limit),
        sort: 'sold_quantity',
    });

    const response = await fetch(
        `${ML_API_URL}/sites/MLB/search?${params.toString()}`,
        { headers: getHeaders(), mode: 'cors' }
    );

    if (!response.ok) return [];
    const data = await response.json();
    return (data.results ?? []).map(mapItem);
}
