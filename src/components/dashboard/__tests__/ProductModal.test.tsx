import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ProductModal } from '../ProductModal';

describe('ProductModal Component', () => {
    const mockOnClose = vi.fn();
    const mockOnSave = vi.fn();

    const defaultProps = {
        isOpen: true,
        onClose: mockOnClose,
        onSave: mockOnSave,
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should not render when isOpen is false', () => {
        render(<ProductModal {...defaultProps} isOpen={false} />);
        expect(screen.queryByText('Adicionar Produto')).not.toBeInTheDocument();
    });

    it('should render create mode when no product is provided', () => {
        render(<ProductModal {...defaultProps} />);
        expect(screen.getByText('Adicionar Produto')).toBeInTheDocument();
    });

    it('should render edit mode when product is provided', () => {
        const product = {
            id: 1,
            name: 'Produto Teste',
            store: 'shopee',
            affiliate_url: 'https://example.com',
            current_price: 99.90,
        };

        render(<ProductModal {...defaultProps} product={product} />);
        expect(screen.getByText('Editar Produto')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Produto Teste')).toBeInTheDocument();
    });

    it('should call onClose when cancel button is clicked', () => {
        render(<ProductModal {...defaultProps} />);

        const cancelButton = screen.getByText('Cancelar');
        fireEvent.click(cancelButton);

        expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should validate required fields', async () => {
        render(<ProductModal {...defaultProps} />);

        const saveButton = screen.getByText('Salvar');
        fireEvent.click(saveButton);

        // Should show validation errors
        await waitFor(() => {
            expect(screen.getByText(/nome é obrigatório/i)).toBeInTheDocument();
        });

        expect(mockOnSave).not.toHaveBeenCalled();
    });

    it('should call onSave with form data when valid', async () => {
        mockOnSave.mockResolvedValue(true);
        render(<ProductModal {...defaultProps} />);

        // Fill in required fields
        const nameInput = screen.getByLabelText(/nome/i);
        const storeSelect = screen.getByLabelText(/loja/i);
        const urlInput = screen.getByLabelText(/url/i);

        fireEvent.change(nameInput, { target: { value: 'Novo Produto' } });
        fireEvent.change(storeSelect, { target: { value: 'shopee' } });
        fireEvent.change(urlInput, { target: { value: 'https://example.com' } });

        const saveButton = screen.getByText('Salvar');
        fireEvent.click(saveButton);

        await waitFor(() => {
            expect(mockOnSave).toHaveBeenCalledWith(
                expect.objectContaining({
                    name: 'Novo Produto',
                    store: 'shopee',
                    affiliate_url: 'https://example.com',
                })
            );
        });
    });

    it('should close modal after successful save', async () => {
        mockOnSave.mockResolvedValue(true);
        render(<ProductModal {...defaultProps} />);

        // Fill in and submit form
        const nameInput = screen.getByLabelText(/nome/i);
        fireEvent.change(nameInput, { target: { value: 'Produto' } });

        const saveButton = screen.getByText('Salvar');
        fireEvent.click(saveButton);

        await waitFor(() => {
            expect(mockOnClose).toHaveBeenCalled();
        });
    });
});
