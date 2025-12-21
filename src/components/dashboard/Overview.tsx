import { useEffect, useState } from "react";
import { Link as LinkIcon, Globe, Tag, Send, Activity, Zap, PieChart } from "lucide-react";
import { api } from "../../services/api";
import { DashboardStats } from "../../types";
import { Skeleton } from "../ui/Skeleton";
import { PageTransition } from "../layout/PageTransition";

export const Overview = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            // Simulate slight delay for skeleton demo
            await new Promise(r => setTimeout(r, 800));

            const data = await api.get<DashboardStats>('/stats/dashboard');
            if (data) {
                setStats(data);
            } else {
                setStats({
                    total_products: 1500,
                    active_products: 1245,
                    connected_stores: 7,
                    active_coupons: 84,
                    telegram_sends: 4230
                });
            }
            setLoading(false);
        };
        fetchStats();
    }, []);

    return (
        <PageTransition>
            <div className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    <StatCard
                        title="Produtos Ativos"
                        value={stats?.active_products?.toLocaleString()}
                        change="+24"
                        icon={<LinkIcon className="text-blue-500" />}
                        loading={loading}
                    />
                    <StatCard
                        title="Lojas Conectadas"
                        value={stats?.connected_stores}
                        change="+1"
                        icon={<Globe className="text-purple-500" />}
                        loading={loading}
                    />
                    <StatCard
                        title="Cupons Ativos"
                        value={stats?.active_coupons}
                        change="+12"
                        icon={<Tag className="text-pink-500" />}
                        loading={loading}
                    />
                    <StatCard
                        title="Envios Telegram"
                        value={stats?.telegram_sends?.toLocaleString()}
                        change="+185"
                        icon={<Send className="text-indigo-500" />}
                        loading={loading}
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Funnel Chart - Keeping static for now, usually would skeleton too */}
                    <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
                        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-indigo-500" />
                            Funil de Vendas (Últimos 30 dias)
                        </h3>
                        {loading ? (
                            <div className="h-64 flex items-end justify-between gap-2 px-2">
                                {[...Array(12)].map((_, i) => (
                                    <Skeleton key={i} className="w-full rounded-t-sm" style={{ height: `${Math.random() * 60 + 20}%` }} />
                                ))}
                            </div>
                        ) : (
                            <div className="h-64 flex items-end justify-between gap-2 px-2">
                                {[40, 65, 45, 80, 55, 90, 70, 85, 60, 75, 50, 95].map((h, i) => (
                                    <div key={i} className="w-full bg-indigo-100 dark:bg-indigo-900/20 rounded-t-sm relative group cursor-pointer hover:bg-indigo-200 dark:hover:bg-indigo-900/40 transition-colors">
                                        <div
                                            className="absolute bottom-0 left-0 right-0 bg-indigo-500 rounded-t-sm transition-all duration-500"
                                            style={{ height: `${h}%` }}
                                        >
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                        <div className="flex justify-between mt-4 text-xs text-slate-500 uppercase tracking-wide">
                            <span>Jan</span><span>Fev</span><span>Mar</span><span>Abr</span><span>Mai</span><span>Jun</span>
                            <span>Jul</span><span>Ago</span><span>Set</span><span>Out</span><span>Nov</span><span>Dez</span>
                        </div>
                    </div>

                    {/* Store Distribution */}
                    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
                        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                            <PieChart className="w-5 h-5 text-purple-500" />
                            Distribuição por Loja
                        </h3>
                        <div className="space-y-4">
                            {loading ? (
                                <>
                                    <Skeleton className="h-6 w-full" />
                                    <Skeleton className="h-6 w-full" />
                                    <Skeleton className="h-6 w-full" />
                                    <Skeleton className="h-6 w-full" />
                                    <Skeleton className="h-6 w-full" />
                                </>
                            ) : (
                                <>
                                    <StoreProgress store="Shopee" value={40} color="bg-orange-500" />
                                    <StoreProgress store="AliExpress" value={20} color="bg-red-500" />
                                    <StoreProgress store="Amazon" value={15} color="bg-yellow-500" />
                                    <StoreProgress store="Mercado Livre" value={10} color="bg-blue-500" />
                                    <StoreProgress store="Outras" value={15} color="bg-pink-500" />
                                </>
                            )}
                        </div>

                        <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800">
                            <div className="text-sm text-slate-500 mb-2">Resumo da Carteira</div>
                            <div className="flex justify-between items-center">
                                {loading ? (
                                    <Skeleton className="h-8 w-24" />
                                ) : (
                                    <span className="font-semibold text-2xl">{stats?.active_products?.toLocaleString()}</span>
                                )}
                                <span className="text-sm bg-green-100 dark:bg-green-900/30 text-green-600 px-2 py-1 rounded">Produtos Ativos</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </PageTransition>
    );
};

const StoreProgress = ({ store, value, color }: any) => (
    <div>
        <div className="flex justify-between text-sm mb-1">
            <span className="font-medium text-slate-700 dark:text-slate-300">{store}</span>
            <span className="text-slate-500">{value}%</span>
        </div>
        <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div className={`h-full ${color} rounded-full`} style={{ width: `${value}%` }} />
        </div>
    </div>
);

const StatCard = ({ title, value, change, icon, loading }: any) => (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 flex items-start justify-between">
        <div className="w-full">
            <p className="text-slate-500 text-sm font-medium mb-1">{title}</p>
            {loading ? (
                <Skeleton className="h-8 w-1/2 my-1" />
            ) : (
                <h3 className="text-2xl font-bold">{value}</h3>
            )}
            <span className="text-emerald-500 text-xs font-semibold flex items-center mt-2">
                <Zap className="w-3 h-3 mr-1" />
                {change} esta semana
            </span>
        </div>
        <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 ml-4">
            {icon}
        </div>
    </div>
);
