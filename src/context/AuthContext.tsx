import React, { createContext, useContext, useState, useEffect } from "react";
import { toast } from "sonner";
import { api } from "../services/api";

interface User {
    id: string | number;
    name: string;
    email: string;
    role: string;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<boolean>;
    logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check local storage on load
        const storedUser = localStorage.getItem("afiliadobot_user");
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch (e) {
                console.error("Failed to parse user from storage", e);
            }
        }
        setLoading(false);
    }, []);

    const login = async (email: string, password: string): Promise<boolean> => {
        try {
            // Call the real backend API
            const res = await api.post<any>('/auth/login', { email, password });

            if (res && res.access_token) {
                const userData = res.user;
                const userObj: User = {
                    id: userData.id,
                    name: userData.name,
                    email: userData.email,
                    role: userData.role
                };

                setUser(userObj);
                localStorage.setItem("afiliadobot_user", JSON.stringify(userObj));
                // Also ensure token is stored for future requests if we had an interceptor
                localStorage.setItem("afiliadobot_token", res.access_token);

                toast.success(`Bem-vindo, ${userObj.name}!`);
                return true;
            }
        } catch (e) {
            console.error(e);
        }

        // toast handled in api.ts or here
        // toast.error("Credenciais inválidas"); 
        return false;
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem("afiliadobot_user");
        localStorage.removeItem("afiliadobot_token");
        toast.info("Sessão encerrada");
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};


