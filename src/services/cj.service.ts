import { api } from "./api";

// ==================== TYPES ====================

export interface CJLink {
  link_id: string;
  title: string;
  description: string;
  advertiser_id: string;
  advertiser_name: string;
  promotion_type: string;
  click_url: string;
  image_url: string;
  coupon_code?: string;
  sale_price?: number;
  original_price?: number;
  currency: string;
  discount?: number;
  start_date?: string;
  end_date?: string;
}

export interface CJAdvertiser {
  id: string;
  name: string;
  primaryUrl?: string;
  logoUrl?: string;
  category?: string;
  country?: string;
  currency?: string;
  averageCommission?: number;
  joined?: boolean;
  programTerms?: Array<{
    id: string;
    name: string;
    status: string;
    commissionType: string;
    commissionBased: string;
    commissionAmount?: number;
    paidOnSales?: boolean;
  }>;
}

export interface CJSearchResult {
  total: number;
  count: number;
  page: number;
  page_size: number;
  items: CJLink[];
}

export interface CJAdvertisersResult {
  total: number;
  count: number;
  page: number;
  page_size: number;
  membership_status: string;
  items: CJAdvertiser[];
}

export interface CJStatus {
  configured: boolean;
  company_id: string;
  token_set: boolean;
  total_advertisers?: number;
  error?: string;
}

export interface CJBroadcastPayload {
  title: string;
  description?: string;
  click_url: string;
  image_url?: string;
  advertiser_name?: string;
  coupon_code?: string;
  sale_price?: number;
  original_price?: number;
  currency?: string;
  promotion_type?: string;
}

// ==================== SERVICE ====================

export const cjService = {
  getStatus: async (): Promise<CJStatus | null> => {
    return await api.get<CJStatus>("/cj/status");
  },

  getStatusLive: async (): Promise<CJStatus | null> => {
    return await api.get<CJStatus>("/cj/status/live");
  },

  searchLinks: async (params?: {
    keywords?: string;
    advertiser_ids?: string;
    page?: number;
    page_size?: number;
  }): Promise<CJSearchResult | null> => {
    const qs = new URLSearchParams();
    if (params?.keywords) qs.append("keywords", params.keywords);
    if (params?.advertiser_ids) qs.append("advertiser_ids", params.advertiser_ids);
    if (params?.page) qs.append("page", String(params.page));
    if (params?.page_size) qs.append("page_size", String(params.page_size));
    return await api.get<CJSearchResult>(`/cj/links?${qs.toString()}`);
  },

  getAdvertisers: async (params?: {
    relationship_status?: string;
    page?: number;
    page_size?: number;
  }): Promise<CJAdvertisersResult | null> => {
    const qs = new URLSearchParams();
    if (params?.relationship_status) qs.append("relationship_status", params.relationship_status);
    if (params?.page) qs.append("page", String(params.page));
    if (params?.page_size) qs.append("page_size", String(params.page_size));
    return await api.get<CJAdvertisersResult>(`/cj/advertisers?${qs.toString()}`);
  },

  getFeeds: async (): Promise<{ total: number; count: number; items: any[] } | null> => {
    return await api.get("/cj/feeds");
  },

  broadcast: async (payload: CJBroadcastPayload): Promise<{ status: string; message: string } | null> => {
    return await api.post("/cj/broadcast", payload);
  },
};
