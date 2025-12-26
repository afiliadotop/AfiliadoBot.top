import { api } from "./api";

export const importService = {
    uploadCsv: async (file: File, store: string = "shopee") => {
        const formData = new FormData();
        formData.append('file', file);

        // Note: api.post uses JSON.stringify by default which breaks FormData.
        // We need to bypass the default api.post for multipart/form-data or modify api.ts to handle it.
        // For now, implementing a direct fetch here or assuming api.post can be adjusted later.

        // Custom implementation to handle FormData since generic api wrapper sets 'Content-Type': 'application/json'
        const token = localStorage.getItem('afiliadobot_token');
        const headers: HeadersInit = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Do NOT set Content-Type for FormData, browser sets it with boundary

        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || '/api'}/import/csv?store=${store}`, {
                method: 'POST',
                headers,
                body: formData
            });

            if (!res.ok) {
                throw new Error(res.statusText);
            }
            return await res.json();
        } catch (e) {
            console.error(e);
            throw e;
        }
    }
};
