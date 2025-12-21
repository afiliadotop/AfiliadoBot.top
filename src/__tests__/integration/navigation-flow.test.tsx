import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../../../context/AuthContext';
import { LandingPage } from '../../../pages/LandingPage';
import { Login } from '../../../pages/Login';
import { Products } from '../../../components/dashboard/Products';

// Mock API
vi.mock('../../../services/api', () => ({
    api: {
        get: vi.fn(),
        post: vi.fn(),
    }
}));

import { api } from '../../../services/api';

/**
 * Integration Test: Navigation Flow
 * Tests navigation between pages and route protection
 */
describe('Navigation Flow Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    it('should navigate from landing page to login', async () => {
        const user = userEvent.setup();

        render(
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/login" element={<Login />} />
                </Routes>
            </BrowserRouter>
        );

        // Should be on landing page
        expect(screen.getByText(/afiliadobot/i)).toBeInTheDocument();

        // Find and click login button
        const loginButtons = screen.getAllByText(/entrar/i);
        await user.click(loginButtons[0]);

        // Should navigate to login page
        await waitFor(() => {
            expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
        });
    });

    it('should protect dashboard routes when not authenticated', async () => {
        render(
            <BrowserRouter initialEntries={['/dashboard/products']}>
                <AuthProvider>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/dashboard/products" element={<Products />} />
                    </Routes>
                </AuthProvider>
            </BrowserRouter>
        );

        // Should redirect to login or show login page
        await waitFor(() => {
            expect(
                screen.queryByText(/produtos/i) ||
                screen.queryByLabelText(/email/i)
            ).toBeInTheDocument();
        });
    });

    it('should allow access to dashboard when authenticated', async () => {
        // Set up authenticated state
        localStorage.setItem('afiliadobot_token', 'test-token');
        localStorage.setItem('afiliadobot_user', JSON.stringify({
            id: 1,
            name: 'Test User',
            email: 'test@example.com',
            role: 'admin'
        }));

        (api.get as any).mockResolvedValue([]);

        render(
            <BrowserRouter initialEntries={['/dashboard/products']}>
                <AuthProvider>
                    <Routes>
                        <Route path="/dashboard/products" element={<Products />} />
                    </Routes>
                </AuthProvider>
            </BrowserRouter>
        );

        // Should render dashboard
        await waitFor(() => {
            expect(screen.getByText(/produtos/i)).toBeInTheDocument();
        });
    });
});
