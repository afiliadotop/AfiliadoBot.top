import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Products } from '../../../components/dashboard/Products';

// Mock API
vi.mock('../../../services/api', () => ({
    api: {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
    }
}));

import { api } from '../../../services/api';

/**
 * Integration Test: Product Management Flow
 * Tests the complete product CRUD flow involving:
 * - Products list display
 * - ProductModal component
 * - useProducts hook
 * - API service calls
 * - State updates
 */
describe('Product Management Flow Integration', () => {
    const mockProducts = [
        {
            id: 1,
            name: 'Smartphone Samsung',
            store: 'shopee',
            category: 'Eletrônicos',
            current_price: 1299.90,
            discount_percentage: 15,
            affiliate_url: 'https://shopee.com/product1'
        },
        {
            id: 2,
            name: 'Fone Bluetooth',
            store: 'amazon',
            category: 'Eletrônicos',
            current_price: 299.90,
            discount_percentage: 10,
            affiliate_url: 'https://amazon.com/product2'
        }
    ];

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should display products list on load', async () => {
        (api.get as any).mockResolvedValue(mockProducts);

        render(
            <BrowserRouter>
                <Products />
            </BrowserRouter>
        );

        // Should show loading initially
        expect(screen.getAllByText(/carregando/i).length).toBeGreaterThan(0);

        // Wait for products to load
        await waitFor(() => {
            expect(screen.getByText('Smartphone Samsung')).toBeInTheDocument();
            expect(screen.getByText('Fone Bluetooth')).toBeInTheDocument();
        });

        // Verify API was called
        expect(api.get).toHaveBeenCalledWith('/products');
    });

    it('should complete create product flow', async () => {
        const user = userEvent.setup();

        // Initial empty list
        (api.get as any).mockResolvedValue([]);

        render(
            <BrowserRouter>
                <Products />
            </BrowserRouter>
        );

        await waitFor(() => {
            expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
        });

        // Click "Add Manually" button
        const addButton = screen.getByText(/adicionar manualmente/i);
        await user.click(addButton);

        // Modal should open
        await waitFor(() => {
            expect(screen.getByText(/adicionar produto/i)).toBeInTheDocument();
        });

        // Fill form
        const nameInput = screen.getByLabelText(/nome/i);
        const storeSelect = screen.getByLabelText(/loja/i);
        const urlInput = screen.getByLabelText(/url/i);

        await user.type(nameInput, 'Novo Produto Teste');
        await user.selectOptions(storeSelect, 'shopee');
        await user.type(urlInput, 'https://shopee.com/test');

        // Mock successful create
        const newProduct = {
            id: 3,
            name: 'Novo Produto Teste',
            store: 'shopee',
            affiliate_url: 'https://shopee.com/test'
        };
        (api.post as any).mockResolvedValue(newProduct);
        (api.get as any).mockResolvedValue([newProduct]);

        // Submit form
        const saveButton = screen.getByText(/salvar/i);
        await user.click(saveButton);

        // Verify API was called
        await waitFor(() => {
            expect(api.post).toHaveBeenCalledWith(
                '/products',
                expect.objectContaining({
                    name: 'Novo Produto Teste',
                    store: 'shopee'
                })
            );
        });
    });

    it('should complete edit product flow', async () => {
        const user = userEvent.setup();
        (api.get as any).mockResolvedValue(mockProducts);

        render(
            <BrowserRouter>
                <Products />
            </BrowserRouter>
        );

        // Wait for products to load
        await waitFor(() => {
            expect(screen.getByText('Smartphone Samsung')).toBeInTheDocument();
        });

        // Find and click edit button for first product
        const editButtons = screen.getAllByLabelText(/editar produto/i);
        await user.click(editButtons[0]);

        // Modal should open with product data
        await waitFor(() => {
            expect(screen.getByDisplayValue('Smartphone Samsung')).toBeInTheDocument();
        });

        // Edit the name
        const nameInput = screen.getByLabelText(/nome/i);
        await user.clear(nameInput);
        await user.type(nameInput, 'Smartphone Samsung Updated');

        // Mock successful update
        const updatedProduct = { ...mockProducts[0], name: 'Smartphone Samsung Updated' };
        (api.put as any).mockResolvedValue(updatedProduct);
        (api.get as any).mockResolvedValue([updatedProduct, mockProducts[1]]);

        // Save changes
        const saveButton = screen.getByText(/salvar/i);
        await user.click(saveButton);

        // Verify API was called
        await waitFor(() => {
            expect(api.put).toHaveBeenCalledWith(
                '/products/1',
                expect.objectContaining({
                    name: 'Smartphone Samsung Updated'
                })
            );
        });
    });

    it('should complete delete product flow', async () => {
        const user = userEvent.setup();
        (api.get as any).mockResolvedValue(mockProducts);

        // Mock window.confirm
        vi.spyOn(window, 'confirm').mockReturnValue(true);

        render(
            <BrowserRouter>
                <Products />
            </BrowserRouter>
        );

        // Wait for products to load
        await waitFor(() => {
            expect(screen.getByText('Smartphone Samsung')).toBeInTheDocument();
        });

        // Mock successful delete
        (api.delete as any).mockResolvedValue({ success: true });
        (api.get as any).mockResolvedValue([mockProducts[1]]);

        // Click delete button
        const deleteButtons = screen.getAllByLabelText(/deletar produto/i);
        await user.click(deleteButtons[0]);

        // Verify API was called
        await waitFor(() => {
            expect(api.delete).toHaveBeenCalledWith('/products/1');
        });

        // Restore confirm
        vi.restoreAllMocks();
    });

    it('should filter products by search term', async () => {
        const user = userEvent.setup();
        (api.get as any).mockResolvedValue(mockProducts);

        render(
            <BrowserRouter>
                <Products />
            </BrowserRouter>
        );

        // Wait for products to load
        await waitFor(() => {
            expect(screen.getByText('Smartphone Samsung')).toBeInTheDocument();
            expect(screen.getByText('Fone Bluetooth')).toBeInTheDocument();
        });

        // Type in search box
        const searchInput = screen.getByPlaceholderText(/buscar produtos/i);
        await user.type(searchInput, 'Smartphone');

        // Only matching product should be visible
        await waitFor(() => {
            expect(screen.getByText('Smartphone Samsung')).toBeInTheDocument();
            expect(screen.queryByText('Fone Bluetooth')).not.toBeInTheDocument();
        });
    });

    it('should show empty state when no products', async () => {
        (api.get as any).mockResolvedValue([]);

        render(
            <BrowserRouter>
                <Products />
            </BrowserRouter>
        );

        await waitFor(() => {
            expect(screen.getByText(/nenhum produto encontrado/i)).toBeInTheDocument();
        });

        // Should show action button
        expect(screen.getByText(/adicionar primeiro produto/i)).toBeInTheDocument();
    });
});
