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

    const [topSales, setTopSales] = useState<ShopeeProduct[]>([]);
    const [topPopular, setTopPopular] = useState<ShopeeProduct[]>([]);
    const [sendingId, setSendingId] = useState<number | null>(null);

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
            const [statsData, syncData, topCommData, topSalesData, topPopularData, rateLimitData] = await Promise.all([
                shopeeService.getStats(),
                shopeeService.getSyncStatus(),
                shopeeService.getTopCommission(10),
                shopeeService.getTopSales(10),
                shopeeService.getTopPopular(10),
                shopeeService.getRateLimitStatus()
            ]);

            if (statsData) setStats(statsData);
            if (syncData) setSyncStatus(syncData);
            if (topCommData) setTopProducts(topCommData.products);
            if (topSalesData) setTopSales(topSalesData.products);
            if (topPopularData) setTopPopular(topPopularData.products);
            if (rateLimitData) setRateLimitStatus(rateLimitData);
        } catch (error) {
            console.error("Error loading admin data:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSendToTelegram = async (product: ShopeeProduct) => {
        setSendingId(product.itemId);
        try {
            const result = await shopeeService.sendProductToTelegram(product.itemId, product);
            if (result?.success) {
                alert(`Produto enviado com sucesso!\n${result.message}`);
            }
        } catch (error: any) {
            alert(`Erro ao enviar: ${error.message || 'Erro desconhecido'}`);
        } finally {
            setSendingId(null);
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

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Top Commission Products */}
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                            <h2 className="text-lg font-semibold mb-4 text-orange-400">
                                🔥 Top 10 - Maior Comissão
                            </h2>
                            <ProductsList
                                products={topProducts}
                                type="commission"
                                onSendTelegram={handleSendToTelegram}
                                sendingId={sendingId}
                            />
                        </div>

                        {/* Top Sales Products */}
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                            <h2 className="text-lg font-semibold mb-4 text-blue-400">
                                🛍️ Top 10 - Mais Vendidos
                            </h2>
                            <ProductsList
                                products={topSales}
                                type="sales"
                                onSendTelegram={handleSendToTelegram}
                                sendingId={sendingId}
                            />
                        </div>

                        {/* Most Popular/Searched Products */}
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 lg:col-span-2">
                            <h2 className="text-lg font-semibold mb-4 text-purple-400">
                                🔍 Top 10 - Mais Pesquisados / Populares
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <ProductsList
                                    products={topPopular}
                                    type="popular"
                                    onSendTelegram={handleSendToTelegram}
                                    sendingId={sendingId}
                                    isGrid
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </PageTransition>
    );
};

// Reusable Products List Component
const ProductsList = ({ products, type, onSendTelegram, sendingId, isGrid = false }: any) => {
    if (!products || products.length === 0) {
        return (
            <div className="text-center py-8 text-slate-400 bg-slate-800/20 rounded-lg">
                Nenhum produto encontrado
            </div>
        );
    }

    const Container = isGrid ? React.Fragment : 'div';
    const Wrapper = isGrid ? 'contents' : 'div';

    // If grid, we just map directly. If list (default), we wrap in a div with space-y-3
    if (isGrid) {
        return (
            <>
                {products.map((product: any, index: number) => (
                    <ProductItem
                        key={product.itemId}
                        product={product}
                        index={index}
                        type={type}
                        onSendTelegram={onSendTelegram}
                        sendingId={sendingId}
                    />
                ))}
            </>
        );
    }

    return (
        <div className="space-y-3">
            {products.map((product: any, index: number) => (
                <ProductItem
                    key={product.itemId}
                    product={product}
                    index={index}
                    type={type}
                    onSendTelegram={onSendTelegram}
                    sendingId={sendingId}
                />
            ))}
        </div>
    );
};

const ProductItem = ({ product, index, type, onSendTelegram, sendingId }: any) => {
    const commission = product.commissionRate ? parseFloat(product.commissionRate) * 100 : 0;

    // Determine what to show on the right side based on type
    const rightSideContent = () => {
        if (type === 'commission') {
            return (
                <div className="text-right">
                    <div className="text-lg font-bold text-green-400">
                        {commission.toFixed(1)}%
                    </div>
                    <div className="text-xs text-green-300">
                        Comissão
                    </div>
                </div>
            );
        } else if (type === 'sales') {
            return (
                <div className="text-right">
                    <div className="text-lg font-bold text-blue-400">
                        {product.sales}
                    </div>
                    <div className="text-xs text-blue-300">
                        Vendas
                    </div>
                </div>
            );
        } else {
            return (
                <div className="text-right">
                    <div className="text-lg font-bold text-purple-400">
                        {product.review_count || product.rating || '-'}
                    </div>
                    <div className="text-xs text-purple-300">
                        Reviews
                    </div>
                </div>
            );
        }
    };

    return (
        <div className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors group">
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
                <div className="font-medium truncate" title={product.productName}>
                    {product.productName}
                </div>
                <div className="text-xs text-slate-400">
                    R$ {product.priceMin} • {(product.sales || 0).toLocaleString()} vendidos
                </div>
            </div>

            {rightSideContent()}

            {/* Telegram Button - Visible on hover or always if mobile */}
            <button
                onClick={() => onSendTelegram(product)}
                disabled={sendingId === product.itemId}
                className="ml-2 p-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-full transition-all opacity-0 group-hover:opacity-100"
                title="Enviar para Telegram"
            >
                {sendingId === product.itemId ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                )}
            </button>
        </div>
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
