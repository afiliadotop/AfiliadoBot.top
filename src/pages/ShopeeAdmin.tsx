import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { shopeeService, ShopeeStats, ShopeeSyncStatus, ShopeeProduct } from '../services/shopee.service';
import { PageTransition } from '../components/layout/PageTransition';
import {
    Package, TrendingUp, DollarSign, Download,
    Clock, AlertCircle, Loader2, Activity, ShieldCheck
} from 'lucide-react';
import { Navigate } from 'react-router-dom';

export const ShopeeAdmin = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState<ShopeeStats | null>(null);
    const [syncStatus, setSyncStatus] = useState<ShopeeSyncStatus | null>(null);
    const [topProducts, setTopProducts] = useState<ShopeeProduct[]>([]);
    const [rateLimitStatus, setRateLimitStatus] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    // Redirect if not admin
    if (user?.role !== 'admin') {
        return <Navigate to="/shopee" replace />;
    }

    useEffect(() => {
        loadAdminData();
    }, []);

    const loadAdminData = async () => {
        setLoading(true);

        try {
            const [statsData, syncData, topData, rateLimitData] = await Promise.all([
                shopeeService.getStats(),
                shopeeService.getSyncStatus(),
                shopeeService.getTopCommission(10),
                shopeeService.getRateLimitStatus()
            ]);

            if (statsData) setStats(statsData);
            if (syncData) setSyncStatus(syncData);
            if (topData) setTopProducts(topData.products);
            if (rateLimitData) setRateLimitStatus(rateLimitData);
        } catch (error) {
            console.error("Error loading admin data:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
            </div>
        );
    }

    return (
        <PageTransition>
            <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
                <div className="max-w-7xl mx-auto space-y-8">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-400 to-orange-600 bg-clip-text text-transparent">
                                📊 Shopee Admin Dashboard
                            </h1>
                            <p className="text-slate-400 mt-1">
                                Estatísticas e controle completo da integração Shopee
                            </p>
                        </div>
                        <button
                            onClick={loadAdminData}
                            className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg hover:bg-slate-800 transition-colors"
                        >
                            <Activity className="w-4 h-4" />
                            Atualizar
                        </button>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <StatCard
                            title="Total Produtos"
                            value={stats?.totalProducts || 0}
                            icon={<Package className="w-6 h-6" />}
                            color="blue"
                        />
                        <StatCard
                            title="Comissão Média"
                            value={`${(stats?.avgCommission || 0).toFixed(1)}%`}
                            icon={<DollarSign className="w-6 h-6" />}
                            color="green"
                        />
                        <StatCard
                            title="Top Comissão"
                            value={`${(stats?.topCommission || 0).toFixed(1)}%`}
                            icon={<TrendingUp className="w-6 h-6" />}
                            color="yellow"
                            highlight
                        />
                        <StatCard
                            title="Importados Hoje"
                            value={stats?.todayImports || 0}
                            icon={<Download className="w-6 h-6" />}
                            color="purple"
                        />
                    </div>

                    {/* Rate Limit Status */}
                    {rateLimitStatus && (
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-lg font-semibold flex items-center gap-2">
                                    <ShieldCheck className="w-5 h-5 text-green-400" />
                                    Rate Limiting Status
                                </h2>
                                <span className="text-sm text-slate-400">
                                    {rateLimitStatus.remaining} requests restantes
                                </span>
                            </div>

                            <div className="space-y-3">
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-400">Usadas / Total:</span>
                                    <span className="font-medium">
                                        {rateLimitStatus.used} / {rateLimitStatus.total}
                                    </span>
                                </div>

                                <div className="relative h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className={`absolute top-0 left-0 h-full transition-all ${rateLimitStatus.percentage_used > 80
                                            ? 'bg-red-500'
                                            : rateLimitStatus.percentage_used > 50
                                                ? 'bg-yellow-500'
                                                : 'bg-green-500'
                                            }`}
                                        style={{ width: `${rateLimitStatus.percentage_used}%` }}
                                    />
                                </div>

                                <div className="flex justify-between text-xs text-slate-500">
                                    <span>{rateLimitStatus.percentage_used.toFixed(1)}% usado</span>
                                    <span>Reset em: {Math.floor(rateLimitStatus.reset_in_seconds / 60)}min</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Sync Status */}
                    {syncStatus && (
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <Clock className="w-5 h-5 text-blue-400" />
                                Último Sync
                            </h2>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div>
                                    <div className="text-2xl font-bold text-green-400">
                                        {syncStatus.products_imported}
                                    </div>
                                    <div className="text-xs text-slate-400">Importados</div>
                                </div>
                                <div>
                                    <div className="text-2xl font-bold text-blue-400">
                                        {syncStatus.products_updated}
                                    </div>
                                    <div className="text-xs text-slate-400">Atualizados</div>
                                </div>
                                <div>
                                    <div className="text-2xl font-bold text-red-400">
                                        {syncStatus.errors}
                                    </div>
                                    <div className="text-xs text-slate-400">Erros</div>
                                </div>
                                <div>
                                    <div className="text-sm font-medium text-slate-300">
                                        {new Date(syncStatus.created_at).toLocaleString('pt-BR')}
                                    </div>
                                    <div className="text-xs text-slate-400">Data/Hora</div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Top Commission Products */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h2 className="text-lg font-semibold mb-4">
                            🔥 Top 10 - Maior Comissão
                        </h2>

                        {topProducts.length > 0 ? (
                            <div className="space-y-3">
                                {topProducts.map((product, index) => {
                                    const commission = product.commissionRate ? parseFloat(product.commissionRate) * 100 : 0;
                                    const commissionAmount = product.commissionAmount ? parseFloat(product.commissionAmount) : 0;

                                    return (
                                        <div
                                            key={product.itemId}
                                            className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors"
                                        >
                                            <div className={`text-2xl font-bold ${index === 0 ? 'text-yellow-400' :
                                                index === 1 ? 'text-slate-300' :
                                                    index === 2 ? 'text-orange-400' :
                                                        'text-slate-500'
                                                }`}>
                                                #{index + 1}
                                            </div>

                                            <img
                                                src={product.imageUrl}
                                                alt={product.productName}
                                                className="w-12 h-12 rounded object-cover"
                                            />

                                            <div className="flex-1 min-w-0">
                                                <div className="font-medium truncate">
                                                    {product.productName}
                                                </div>
                                                <div className="text-xs text-slate-400">
                                                    R$ {product.priceMin} • {(product.sales || 0).toLocaleString()} vendidos
                                                </div>
                                            </div>

                                            <div className="text-right">
                                                <div className="text-lg font-bold text-green-400">
                                                    {commission.toFixed(1)}%
                                                </div>
                                                <div className="text-xs text-green-300">
                                                    R$ {commissionAmount.toFixed(2)}
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-slate-400">
                                Nenhum produto encontrado
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </PageTransition>
    );
};

// Stat Card Component
interface StatCardProps {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: 'blue' | 'green' | 'yellow' | 'purple';
    highlight?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, highlight }) => {
    const colorClasses = {
        blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        green: 'bg-green-500/10 text-green-400 border-green-500/20',
        yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
        purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    };

    return (
        <div className={`bg-slate-900 border ${highlight ? 'border-yellow-500/50' : 'border-slate-800'} rounded-xl p-6 ${highlight ? 'ring-2 ring-yellow-500/20' : ''}`}>
            <div className={`inline-flex p-3 rounded-lg mb-4 ${colorClasses[color]}`}>
                {icon}
            </div>
            <div className="space-y-1">
                <div className="text-sm text-slate-400">{title}</div>
                <div className="text-2xl font-bold">{value}</div>
            </div>
        </div>
    );
};
