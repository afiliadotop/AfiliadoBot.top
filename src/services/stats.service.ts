import { api } from "./api";
import { DashboardStats } from "../types";

export const statsService = {
    getDashboardStats: async () => {
        return await api.get<DashboardStats>('/stats/dashboard');
    }
};
