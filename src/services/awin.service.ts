import { api } from "./api";

// ==================== TYPES ====================

export interface AwinProduct {
    id?: string;
    awin_product_id: string;
    advertiser_id: number;
    advertiser_name?: string;
    title: string;
    description?: string;
    link: string;
    image_url?: string;
    price?: number;
    sale_price?: number;
    currency?: string;
    availability?: string;
    brand?: string;
    category?: string;
    condition?: string;
    color?: string;
    size?: string;
    gender?: string;
    affiliate_link?: string;
    is_active?: boolean;
}

export interface AwinOffer {
    // API Frontend mapping fields
    awin_offer_id?: number;
    advertiser_id?: number;
    advertiser_name?: string;
    title: string;
    description?: string;
    promotion_type?: string;
    code?: string;
    discount_value?: number;
    discount_type?: string;
    minimum_order?: number;
    starts_at?: string;
    expires_at?: string;
    deeplink?: string;
    tracking_link?: string;
    is_active?: boolean;

    // Awin Raw fields
    type?: string;
    endDate?: string;
    url?: string;
    urlTracking?: string;
    advertiser?: {
        id: number;
        name: string;
        joined?: boolean;
    };
    promotionId?: number;
}

export interface AwinProgram {
    id?: number;
    name?: string;
    displayName?: string;
    logoUrl?: string;
    primaryRegion?: { countryCode: string };
    currencyCode?: string;
    relationship?: string;
    commissionRate?: number;
}

export interface AwinCommissionGroup {
    id?: number;
    name?: string;
    code?: string;
    type?: string;
    percentage?: number;
    amount?: number;
    currency?: string;
}

export interface AwinPerformanceEntry {
    advertiserId?: number;
    advertiserName?: string;
    impressions?: number;
    clicks?: number;
    transactions?: number;
    commissions?: number;
    currency?: string;
    epc?: number;
    conversionRate?: number;
}

export interface AwinGenerateLinkRequest {
    advertiser_id: number;
    destination_url: string;
    shorten?: boolean;
    campaign?: string;
}

export interface AwinGenerateLinkResponse {
    click_through_url?: string;
    short_url?: string;
    advertiser_id: number;
}

export interface AwinStatus {
    configured: boolean;
    publisher_id: string;
    token_set: boolean;
}

// ==================== SERVICE ====================

export const awinService = {
    // --- Status ---
    getStatus: async (): Promise<AwinStatus | null> => {
        return await api.get<AwinStatus>("/awin/status");
    },

    // --- Link Builder ---
    generateLink: async (request: AwinGenerateLinkRequest): Promise<AwinGenerateLinkResponse | null> => {
        return await api.post<AwinGenerateLinkResponse>("/awin/generate-link", request);
    },

    generateBatchLinks: async (
        links: AwinGenerateLinkRequest[]
    ): Promise<{ count: number; results: any[] } | null> => {
        return await api.post("/awin/batch-links", { links });
    },

    // --- Quota ---
    getQuota: async (): Promise<any | null> => {
        return await api.get("/awin/quota");
    },

    // --- Offers ---
    getOffers: async (params?: {
        advertiser_ids?: number[];
        promotion_types?: string[];
        page?: number;
        page_size?: number;
    }): Promise<{ data?: AwinOffer[]; offers?: AwinOffer[]; total?: number } | null> => {
        return await api.post("/awin/offers", params || {});
    },

    getPublicVouchers: async (): Promise<{ data: AwinOffer[]; cached: boolean } | null> => {
        return await api.get("/awin/public/vouchers");
    },

    // --- Programs ---
    getPrograms: async (relationship: string = "joined"): Promise<{ count: number; programs: AwinProgram[] } | null> => {
        return await api.get(`/awin/programs?relationship=${relationship}`);
    },

    getProgramDetails: async (advertiserId: number): Promise<AwinProgram | null> => {
        return await api.get<AwinProgram>(`/awin/programs/${advertiserId}`);
    },

    // --- Commission Groups ---
    getCommissionGroups: async (advertiserId: number): Promise<{ count: number; groups: AwinCommissionGroup[] } | null> => {
        return await api.get(`/awin/commission-groups/${advertiserId}`);
    },

    // --- Performance ---
    getPerformanceReport: async (params: {
        start_date?: string;
        end_date?: string;
        region?: string;
    }): Promise<{ data: AwinPerformanceEntry[]; period: any } | null> => {
        const qs = new URLSearchParams();
        if (params.start_date) qs.append("start_date", params.start_date);
        if (params.end_date) qs.append("end_date", params.end_date);
        if (params.region) qs.append("region", params.region);
        return await api.get(`/awin/performance?${qs.toString()}`);
    },

    // --- Product Feed ---
    getProductFeed: async (
        advertiserId: number,
        locale: string = "pt_BR",
        maxProducts: number = 200
    ): Promise<{ count: number; products: AwinProduct[] } | null> => {
        return await api.get(`/awin/product-feed/${advertiserId}?locale=${locale}&max_products=${maxProducts}`);
    },
};
