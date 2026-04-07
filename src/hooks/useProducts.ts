import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { supabase } from '../lib/supabase';
import { toast } from 'sonner';

export interface Product {
    id: string | number;
    name: string;
    store: string;
    affiliate_link: string;
    current_price: number;
    original_price?: number;
    discount_percentage?: number;
    category?: string;
    subcategory?: string;
    image_url?: string;
    description?: string;
    rating?: number;
    review_count?: number;
    stock_status?: string;
    coupon_code?: string;
    tags?: string[];
    is_active: boolean;
    is_featured: boolean;
    created_at: string;
    updated_at: string;
}

export interface ProductFilters {
    store?: string;
    category?: string;
    search?: string;
    is_active?: boolean;
}

export const useProducts = (initialFilters: ProductFilters = {}) => {
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState<ProductFilters>(initialFilters);

    const fetchProducts = useCallback(async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (filters.store) params.append('store', filters.store);
            if (filters.category) params.append('category', filters.category);
            if (filters.search) params.append('search', filters.search);
            if (filters.is_active !== undefined) params.append('is_active', String(filters.is_active));

            const response = await api.get<any>(`/products?${params.toString()}`);

            if (response) {
                // Support both Direct Array (legacy) and Object response (modern)
                const data = Array.isArray(response) ? response : (response.data || []);
                setProducts(data);
            }
        } catch (error) {
            console.error('Failed to fetch products:', error);
            toast.error('Erro ao carregar produtos');
        } finally {
            setLoading(false);
        }
    }, [filters]);

    const createProduct = async (productData: Partial<Product>) => {
        try {
            const response = await api.post<Product>('/products', productData);
            if (response) {
                toast.success('Produto criado com sucesso!');
                fetchProducts();
                return response;
            }
        } catch (error) {
            console.error('Failed to create product:', error);
            toast.error('Erro ao criar produto');
            return null;
        }
    };

    const updateProduct = async (id: string | number, productData: Partial<Product>) => {
        try {
            const response = await api.put<Product>(`/products/${id}`, productData);
            if (response) {
                toast.success('Produto atualizado!');
                fetchProducts();
                return response;
            }
        } catch (error) {
            console.error('Failed to update product:', error);
            toast.error('Erro ao atualizar produto');
            return null;
        }
    };

    const deleteProduct = async (id: string | number) => {
        try {
            const response = await api.delete<{ message: string }>(`/products/${id}`);
            if (response) {
                toast.success('Produto deletado!');
                fetchProducts();
                return true;
            }
        } catch (error) {
            console.error('Failed to delete product:', error);
            toast.error('Erro ao deletar produto');
            return false;
        }
    };

    useEffect(() => {
        fetchProducts();

        const channel = supabase
            .channel('public:products')
            .on(
                'postgres_changes',
                { event: '*', schema: 'public', table: 'products' },
                () => fetchProducts()
            )
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, [fetchProducts]);

    return {
        products,
        loading,
        filters,
        setFilters,
        createProduct,
        updateProduct,
        deleteProduct,
        refetch: fetchProducts
    };
};
