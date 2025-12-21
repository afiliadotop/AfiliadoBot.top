import { toast } from 'sonner';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const api = {
    get: async <T>(endpoint: string): Promise<T | null> => {
        try {
            const res = await fetch(`${BASE_URL}${endpoint}`);
            if (!res.ok) {
                throw new Error(`API Error: ${res.status}`);
            }
            return await res.json();
        } catch (e) {
            console.error(e);
            // toast.error('Erro de conexão com o servidor');
            return null;
        }
    },

    post: async <T>(endpoint: string, body: any): Promise<T | null> => {
        try {
            const res = await fetch(`${BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!res.ok) {
                throw new Error(`API Error: ${res.status}`);
            }
            return await res.json();
        } catch (e: any) {
            console.error(e);
            toast.error(e.message || 'Erro ao enviar dados');
            return null;
        }
    }
};
