import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useProducts } from '../useProducts';

// Mock the API
vi.mock('../../services/api', () => ({
    api: {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
    }
}));

import { api } from '../../services/api';

describe('useProducts Hook', () => {
    const mockProducts = [
        {
            id: 1,
            name: 'Produto Teste',
            store: 'shopee',
            category: 'Eletrônicos',
            current_price: 99.90,
            discount_percentage: 10,
            affiliate_url: 'https://example.com',
        }
    ];

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should fetch products on mount', async () => {
        (api.get as any).mockResolvedValue(mockProducts);

        const { result } = renderHook(() => useProducts());

        expect(result.current.loading).toBe(true);

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        expect(result.current.products).toEqual(mockProducts);
        expect(api.get).toHaveBeenCalledWith('/products');
    });

    it('should handle createProduct', async () => {
        const newProduct = { name: 'Novo Produto', store: 'shopee' };
        (api.post as any).mockResolvedValue({ ...newProduct, id: 2 });
        (api.get as any).mockResolvedValue([...mockProducts, { ...newProduct, id: 2 }]);

        const { result } = renderHook(() => useProducts());

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        await result.current.createProduct(newProduct);

        expect(api.post).toHaveBeenCalledWith('/products', newProduct);
    });

    it('should handle updateProduct', async () => {
        const updatedData = { name: 'Produto Atualizado' };
        (api.put as any).mockResolvedValue({ ...mockProducts[0], ...updatedData });
        (api.get as any).mockResolvedValue(mockProducts);

        const { result } = renderHook(() => useProducts());

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        await result.current.updateProduct(1, updatedData);

        expect(api.put).toHaveBeenCalledWith('/products/1', updatedData);
    });

    it('should handle deleteProduct', async () => {
        (api.delete as any).mockResolvedValue({ success: true });
        (api.get as any).mockResolvedValue(mockProducts);

        const { result } = renderHook(() => useProducts());

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        await result.current.deleteProduct(1);

        expect(api.delete).toHaveBeenCalledWith('/products/1');
    });

    it('should return empty array on API error', async () => {
        (api.get as any).mockResolvedValue(null);

        const { result } = renderHook(() => useProducts());

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        expect(result.current.products).toEqual([]);
    });
});
