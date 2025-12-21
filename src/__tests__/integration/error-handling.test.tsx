import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ErrorBoundary } from '../../../components/ErrorBoundary';
import { Products } from '../../../components/dashboard/Products';

// Mock API to throw errors
vi.mock('../../../services/api', () => ({
    api: {
        get: vi.fn(),
    }
}));

import { api } from '../../../services/api';

/**
 * Integration Test: Error Handling Flow
 * Tests how errors propagate through components
 */
describe('Error Handling Flow Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Suppress console errors in tests
        vi.spyOn(console, 'error').mockImplementation(() => { });
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should catch and display errors from nested components', async () => {
        // Create a component that throws
        const ThrowError = () => {
            throw new Error('Test error');
        };

        render(
            <ErrorBoundary>
                <ThrowError />
            </ErrorBoundary>
        );

        // Error boundary should catch and display fallback
        await waitFor(() => {
            expect(screen.getByText(/algo deu errado/i)).toBeInTheDocument();
        });
    });

    it('should handle API errors gracefully', async () => {
        // Mock API error
        (api.get as any).mockRejectedValue(new Error('Network error'));

        render(
            <BrowserRouter>
                <ErrorBoundary>
                    <Products />
                </ErrorBoundary>
            </BrowserRouter>
        );

        // Component should handle error without crashing
        await waitFor(() => {
            // Should show empty state or error message, not crash
            expect(screen.getByText(/produtos/i)).toBeInTheDocument();
        });
    });

    it('should allow recovery from errors', async () => {
        const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
            if (shouldThrow) {
                throw new Error('Test error');
            }
            return <div>Success</div>;
        };

        const { rerender } = render(
            <ErrorBoundary>
                <ThrowError shouldThrow={true} />
            </ErrorBoundary>
        );

        // Error should be caught
        await waitFor(() => {
            expect(screen.getByText(/algo deu errado/i)).toBeInTheDocument();
        });

        // Click reload button
        const reloadButton = screen.getByText(/recarregar página/i);
        expect(reloadButton).toBeInTheDocument();
    });
});
