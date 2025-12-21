import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../api';
import { toast } from 'sonner';

// Mock sonner toast
vi.mock('sonner', () => ({
    toast: {
        error: vi.fn(),
        success: vi.fn(),
    }
}));

// Mock fetch
global.fetch = vi.fn();

describe('API Service', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    describe('GET requests', () => {
        it('should make successful GET request', async () => {
            const mockData = { id: 1, name: 'Test' };
            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: async () => mockData,
            });

            const result = await api.get('/test');

            expect(result).toEqual(mockData);
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/test'),
                expect.objectContaining({
                    headers: expect.objectContaining({
                        'Content-Type': 'application/json',
                    }),
                })
            );
        });

        it('should include Authorization header when token exists', async () => {
            localStorage.setItem('afiliadobot_token', 'test-token');

            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: async () => ({}),
            });

            await api.get('/test');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    headers: expect.objectContaining({
                        'Authorization': 'Bearer test-token',
                    }),
                })
            );
        });

        it('should handle 401 and redirect to login', async () => {
            const mockLocation = { href: '' };
            Object.defineProperty(window, 'location', {
                value: mockLocation,
                writable: true,
            });

            (global.fetch as any).mockResolvedValue({
                ok: false,
                status: 401,
                statusText: 'Unauthorized',
            });

            const result = await api.get('/test');

            expect(result).toBeNull();
            expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('Sessão expirada'));
            expect(mockLocation.href).toBe('/login');
        });

        it('should return null on error', async () => {
            (global.fetch as any).mockRejectedValue(new Error('Network error'));

            const result = await api.get('/test');

            expect(result).toBeNull();
            expect(toast.error).toHaveBeenCalled();
        });
    });

    describe('POST requests', () => {
        it('should make successful POST request', async () => {
            const mockData = { id: 1 };
            const postData = { name: 'Test' };

            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: async () => mockData,
            });

            const result = await api.post('/test', postData);

            expect(result).toEqual(mockData);
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/test'),
                expect.objectContaining({
                    method: 'POST',
                    body: JSON.stringify(postData),
                })
            );
        });

        it('should handle POST errors', async () => {
            (global.fetch as any).mockResolvedValue({
                ok: false,
                status: 400,
                statusText: 'Bad Request',
                json: async () => ({ message: 'Invalid data' }),
            });

            const result = await api.post('/test', {});

            expect(result).toBeNull();
            expect(toast.error).toHaveBeenCalled();
        });
    });

    describe('PUT requests', () => {
        it('should make successful PUT request', async () => {
            const mockData = { id: 1, updated: true };
            const putData = { name: 'Updated' };

            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: async () => mockData,
            });

            const result = await api.put('/test/1', putData);

            expect(result).toEqual(mockData);
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/test/1'),
                expect.objectContaining({
                    method: 'PUT',
                })
            );
        });
    });

    describe('DELETE requests', () => {
        it('should make successful DELETE request', async () => {
            (global.fetch as any).mockResolvedValue({
                ok: true,
                json: async () => ({ success: true }),
            });

            const result = await api.delete('/test/1');

            expect(result).toEqual({ success: true });
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/test/1'),
                expect.objectContaining({
                    method: 'DELETE',
                })
            );
        });
    });
});
