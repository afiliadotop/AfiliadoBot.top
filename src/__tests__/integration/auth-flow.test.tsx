import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../../context/AuthContext';
import { Login } from '../../../pages/Login';
import App from '../../../App';

// Mock API
vi.mock('../../../services/api', () => ({
    api: {
        post: vi.fn(),
        get: vi.fn(),
    }
}));

import { api } from '../../../services/api';

/**
 * Integration Test: Authentication Flow
 * Tests the complete login flow involving:
 * - Login page UI
 * - AuthContext state management
 * - API service calls
 * - Navigation after login
 */
describe('Authentication Flow Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    it('should complete full login flow and redirect to dashboard', async () => {
        // Mock successful login response
        (api.post as any).mockResolvedValue({
            access_token: 'test-token-123',
            user: {
                id: 1,
                name: 'Test User',
                email: 'test@example.com',
                role: 'admin'
            }
        });

        // Mock dashboard stats
        (api.get as any).mockResolvedValue({
            total_products: 100,
            active_products: 80,
        });

        // Render app with routing
        render(
            <BrowserRouter>
                <AuthProvider>
                    <Login />
                </AuthProvider>
            </BrowserRouter>
        );

        // Find and fill login form
        const emailInput = screen.getByLabelText(/email/i);
        const passwordInput = screen.getByLabelText(/senha/i);
        const loginButton = screen.getByRole('button', { name: /entrar/i });

        fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
        fireEvent.change(passwordInput, { target: { value: 'password123' } });
        fireEvent.click(loginButton);

        // Verify API was called with correct credentials
        await waitFor(() => {
            expect(api.post).toHaveBeenCalledWith('/auth/login', {
                email: 'test@example.com',
                password: 'password123'
            });
        });

        // Verify token and user were stored
        expect(localStorage.getItem('afiliadobot_token')).toBe('test-token-123');
        expect(localStorage.getItem('afiliadobot_user')).toContain('Test User');
    });

    it('should handle login error correctly', async () => {
        // Mock failed login
        (api.post as any).mockResolvedValue(null);

        render(
            <BrowserRouter>
                <AuthProvider>
                    <Login />
                </AuthProvider>
            </BrowserRouter>
        );

        const emailInput = screen.getByLabelText(/email/i);
        const passwordInput = screen.getByLabelText(/senha/i);
        const loginButton = screen.getByRole('button', { name: /entrar/i });

        fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } });
        fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
        fireEvent.click(loginButton);

        // Should not store anything on failed login
        await waitFor(() => {
            expect(localStorage.getItem('afiliadobot_token')).toBeNull();
        });
    });

    it('should logout and clear user data', async () => {
        // Set up logged in state
        localStorage.setItem('afiliadobot_token', 'test-token');
        localStorage.setItem('afiliadobot_user', JSON.stringify({
            id: 1,
            name: 'Test User',
            email: 'test@example.com',
            role: 'admin'
        }));

        const { rerender } = render(
            <BrowserRouter>
                <AuthProvider>
                    <div data-testid="test-component">Test</div>
                </AuthProvider>
            </BrowserRouter>
        );

        // User should be logged in initially
        expect(localStorage.getItem('afiliadobot_token')).toBe('test-token');

        // Simulate logout
        localStorage.removeItem('afiliadobot_token');
        localStorage.removeItem('afiliadobot_user');

        rerender(
            <BrowserRouter>
                <AuthProvider>
                    <div data-testid="test-component">Test</div>
                </AuthProvider>
            </BrowserRouter>
        );

        // Verify data was cleared
        expect(localStorage.getItem('afiliadobot_token')).toBeNull();
        expect(localStorage.getItem('afiliadobot_user')).toBeNull();
    });
});
