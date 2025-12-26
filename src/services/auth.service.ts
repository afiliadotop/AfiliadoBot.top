import { api } from "./api";
import { User, AuthResponse } from "../types";

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    name: string;
    email: string;
    password: string;
}

export const authService = {
    login: async (credentials: LoginCredentials) => {
        return await api.post<AuthResponse>('/auth/login', credentials);
    },

    register: async (data: RegisterData) => {
        return await api.post<{ success: boolean; message: string; user: User }>('/auth/register', data);
    },

    logout: () => {
        localStorage.removeItem("afiliadobot_user");
        localStorage.removeItem("afiliadobot_token");
        window.location.href = '/login';
    },

    getCurrentUser: (): User | null => {
        const userStr = localStorage.getItem("afiliadobot_user");
        if (userStr) {
            try {
                return JSON.parse(userStr);
            } catch {
                return null;
            }
        }
        return null;
    },

    isAuthenticated: (): boolean => {
        return !!localStorage.getItem("afiliadobot_token");
    }
};
