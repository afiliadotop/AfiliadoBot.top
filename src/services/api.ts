import { toast } from 'sonner';
import * as Sentry from "@sentry/react";

const getBaseUrl = (): string => {
    const url = import.meta.env.VITE_API_URL || '/api';
    // Se a URL for absoluta (contém http) e não termina com /api, adiciona
    if (url.startsWith('http') && !url.endsWith('/api') && !url.includes('/api/')) {
        return url.endsWith('/') ? `${url}api` : `${url}/api`;
    }
    return url;
};

const BASE_URL = getBaseUrl();

// Error logging service
const logError = (error: Error, context?: string) => {
    if (import.meta.env.DEV) {
        console.error(context || 'API Error:', error);
    }
    // Setup for Sentry
    if (import.meta.env.PROD) {
        Sentry.captureException(error, {
            tags: { context },
            extra: { url: window.location.href }
        });
    }
};

// Get authentication headers
const getHeaders = (): HeadersInit => {
    const token = localStorage.getItem('afiliadobot_token');
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
};

export const api = {
    get: async <T>(endpoint: string): Promise<T | null> => {
        try {
            const res = await fetch(`${BASE_URL}${endpoint}`, {
                headers: getHeaders()
            });

            if (!res.ok) {
                if (res.status === 401) {
                    toast.error('Sessão expirada. Faça login novamente.');
                    localStorage.removeItem('afiliadobot_token');
                    localStorage.removeItem('afiliadobot_user');
                    window.location.href = '/login';
                    return null;
                }
                // Try to get error message from response
                try {
                    const errorData = await res.json();
                    const errorMessage = errorData.detail || errorData.message || 'Erro de conexão';
                    toast.error(errorMessage);
                } catch {
                    toast.error(`Erro: ${res.statusText}`);
                }
                return null;  // Return null on error, don't try to read body again
            }

            return await res.json();
        } catch (e) {
            logError(e as Error, `GET ${endpoint}`);
            toast.error(`Erro de conexão: ${(e as Error).message}`);
            return null;
        }
    },

    post: async <T, B = unknown>(endpoint: string, body?: B, customHeaders?: HeadersInit): Promise<T | null> => {
        try {
            const isFormData = body instanceof FormData;
            const headers = { ...getHeaders(), ...customHeaders };
            
            // If it's FormData, let the browser set the boundary and Content-Type
            if (isFormData) {
                delete (headers as any)['Content-Type'];
            }

            const res = await fetch(`${BASE_URL}${endpoint}`, {
                method: 'POST',
                headers,
                body: isFormData ? (body as any) : JSON.stringify(body || {})
            });

            if (!res.ok) {
                const error = new Error(`HTTP ${res.status}: ${res.statusText}`);
                logError(error, `POST ${endpoint}`);

                if (res.status === 401) {
                    toast.error('Sessão expirada. Faça login novamente.');
                    localStorage.removeItem('afiliadobot_token');
                    localStorage.removeItem('afiliadobot_user');
                    window.location.href = '/login';
                    return null;
                }

                // Try to get error message from response
                try {
                    const errorData = await res.json();
                    const errorMessage = errorData.detail || errorData.message || 'Erro ao enviar dados';
                    toast.error(errorMessage);
                } catch {
                    toast.error('Erro ao enviar dados');
                }
                return null;
            }

            return await res.json();
        } catch (e) {
            logError(e as Error, `POST ${endpoint}`);
            toast.error(`Erro: ${(e as Error).message}`);
            return null;
        }
    },

    put: async <T, B = unknown>(endpoint: string, body?: B): Promise<T | null> => {
        try {
            const res = await fetch(`${BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: getHeaders(),
                body: JSON.stringify(body)
            });

            if (!res.ok) {
                if (res.status === 401) {
                    toast.error('Sessão expirada. Faça login novamente.');
                    localStorage.removeItem('afiliadobot_token');
                    localStorage.removeItem('afiliadobot_user');
                    window.location.href = '/login';
                    return null;
                }
                const error = new Error(`HTTP ${res.status}: ${res.statusText}`);
                logError(error, `PUT ${endpoint}`);

                // Try to get error message from response
                try {
                    const errorData = await res.json();
                    const errorMessage = errorData.detail || errorData.message || `Erro ao atualizar: ${res.statusText}`;
                    toast.error(errorMessage);
                } catch {
                    toast.error(`Erro ao atualizar: ${res.statusText}`);
                }
                return null;
            }

            return await res.json();
        } catch (e) {
            logError(e as Error, `PUT ${endpoint}`);
            toast.error(`Erro: ${(e as Error).message}`);
            return null;
        }
    },

    delete: async <T>(endpoint: string): Promise<T | null> => {
        try {
            const res = await fetch(`${BASE_URL}${endpoint}`, {
                method: 'DELETE',
                headers: getHeaders()
            });

            if (!res.ok) {
                if (res.status === 401) {
                    toast.error('Sessão expirada. Faça login novamente.');
                    localStorage.removeItem('afiliadobot_token');
                    localStorage.removeItem('afiliadobot_user');
                    window.location.href = '/login';
                    return null;
                }
                const error = new Error(`HTTP ${res.status}: ${res.statusText}`);
                logError(error, `DELETE ${endpoint}`);

                // Try to get error message from response
                try {
                    const errorData = await res.json();
                    const errorMessage = errorData.detail || errorData.message || `Erro ao deletar: ${res.statusText}`;
                    toast.error(errorMessage);
                } catch {
                    toast.error(`Erro ao deletar: ${res.statusText}`);
                }
            }

            return await res.json();
        } catch (e) {
            logError(e as Error, `DELETE ${endpoint}`);
            toast.error(`Erro: ${(e as Error).message}`);
            return null;
        }
    }
};
