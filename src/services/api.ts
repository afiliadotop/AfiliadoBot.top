import { toast } from 'sonner';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Error logging service
const logError = (error: Error, context?: string) => {
    if (import.meta.env.DEV) {
        console.error(context || 'API Error:', error);
    }
    // TODO: Send to error tracking service (Sentry/LogRocket)
    // sentry.captureException(error, { tags: { context } });
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
                const error = new Error(`HTTP ${res.status}: ${res.statusText}`);
                logError(error, `GET ${endpoint}`);

                if (res.status === 401) {
                    toast.error('Sessão expirada. Faça login novamente.');
                    // Clear auth data
                    localStorage.removeItem('afiliadobot_token');
                    localStorage.removeItem('afiliadobot_user');
                    window.location.href = '/login';
                }
                return null;
            }

            return await res.json();
        } catch (e) {
            logError(e as Error, `GET ${endpoint}`);
            toast.error('Erro de conexão com o servidor');
            return null;
        }
    },

    post: async <T, B = unknown>(endpoint: string, body: B): Promise<T | null> => {
        try {
            const res = await fetch(`${BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify(body)
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
                    toast.error(errorData.message || 'Erro ao enviar dados');
                } catch {
                    toast.error('Erro ao enviar dados');
                }
                return null;
            }

            return await res.json();
        } catch (e) {
            logError(e as Error, `POST ${endpoint}`);
            toast.error('Erro ao enviar dados');
            return null;
        }
    },

    put: async <T, B = unknown>(endpoint: string, body: B): Promise<T | null> => {
        try {
            const res = await fetch(`${BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: getHeaders(),
                body: JSON.stringify(body)
            });

            if (!res.ok) {
                const error = new Error(`HTTP ${res.status}: ${res.statusText}`);
                logError(error, `PUT ${endpoint}`);

                if (res.status === 401) {
                    toast.error('Sessão expirada. Faça login novamente.');
                    localStorage.removeItem('afiliadobot_token');
                    localStorage.removeItem('afiliadobot_user');
                    window.location.href = '/login';
                    return null;
                }

                toast.error('Erro ao atualizar dados');
                return null;
            }

            return await res.json();
        } catch (e) {
            logError(e as Error, `PUT ${endpoint}`);
            toast.error('Erro ao atualizar dados');
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
                const error = new Error(`HTTP ${res.status}: ${res.statusText}`);
                logError(error, `DELETE ${endpoint}`);

                if (res.status === 401) {
                    toast.error('Sessão expirada. Faça login novamente.');
                    localStorage.removeItem('afiliadobot_token');
                    localStorage.removeItem('afiliadobot_user');
                    window.location.href = '/login';
                    return null;
                }

                toast.error('Erro ao deletar');
                return null;
            }

            return await res.json();
        } catch (e) {
            logError(e as Error, `DELETE ${endpoint}`);
            toast.error('Erro ao deletar');
            return null;
        }
    }
};
