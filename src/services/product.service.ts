import { api } from "./api";
import { Product } from "../types";

export interface ProductFilters {
    store?: string;
    category?: string;
    search?: string;
    is_active?: boolean;
    limit?: number;
    offset?: number;
    min_discount?: number;
}

export interface ProductResponse {
    data: Product[];
    count: number;
}

export const productService = {
    getAll: async (filters: ProductFilters = {}) => {
        // Convert filters to query string
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                params.append(key, String(value));
            }
        });

        return await api.get<ProductResponse>(`/products?${params.toString()}`);
    },

    getById: async (id: string | number) => {
        return await api.get<Product>(`/products/${id}`);
    },

    create: async (product: Partial<Product>) => {
        return await api.post<Product>('/products', product);
    },

    update: async (id: string | number, product: Partial<Product>) => {
        return await api.put<Product>(`/products/${id}`, product);
    },

    delete: async (id: string | number) => {
        return await api.delete<{ message: string }>(`/products/${id}`);
    }
};
