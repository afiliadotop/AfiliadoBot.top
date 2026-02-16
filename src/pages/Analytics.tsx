import { useState, useEffect } from 'react';
import {
    getPerformanceOverview,
    getTopProducts,
    getStoreComparison,
    getTrends,
    type PerformanceOverview,
    type TopProduct,
    type StorePerformance,
    type TrendData,
} from '../services/analyticsService';
import PerformanceCards from '../components/analytics/PerformanceCards';
import PerformanceChart from '../components/analytics/PerformanceChart';
import TopProductsTable from '../components/analytics/TopProductsTable';
import StoreComparison from '../components/analytics/StoreComparison';

export default function Analytics() {
    const [overview, setOverview] = useState<PerformanceOverview | null>(null);
    const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
    const [stores, setStores] = useState<StorePerformance[]>([]);
    const [trends, setTrends] = useState<TrendData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [period, setPeriod] = useState(30);
    const [metric, setMetric] = useState<'clicks' | 'telegram_sends' | 'quality_score'>('clicks');

    useEffect(() => {
        loadAnalytics();
    }, [period, metric]);

    async function loadAnalytics() {
        setLoading(true);
        setError(null);

        try {
            const [overviewData, productsData, storesData, trendsData] = await Promise.all([
                getPerformanceOverview(period),
                getTopProducts(10, metric),
                getStoreComparison(),
                getTrends(period),
            ]);

            setOverview(overviewData);
            setTopProducts(productsData.products);
            setStores(storesData.stores);
            setTrends(trendsData.trends);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load analytics');
            console.error('Analytics error:', err);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600 font-medium">Carregando analytics...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-100">
                <div className="bg-white rounded-lg shadow-xl p-8 max-w-md">
                    <div className="text-red-600 text-5xl mb-4">⚠️</div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">Erro ao Carregar Analytics</h2>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={loadAnalytics}
                        className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition"
                    >
                        Tentar Novamente
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">
                        📊 Performance Analytics
                    </h1>
                    <p className="text-gray-600">
                        Visão completa de performance dos produtos e conversões
                    </p>
                </div>

                {/* Filters */}
                <div className="bg-white rounded-lg shadow-md p-4 mb-6 flex gap-4 items-center">
                    <div className="flex items-center gap-2">
                        <label className="text-sm font-medium text-gray-700">Período:</label>
                        <select
                            value={period}
                            onChange={(e) => setPeriod(Number(e.target.value))}
                            className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        >
                            <option value={7}>Últimos 7 dias</option>
                            <option value={30}>Últimos 30 dias</option>
                            <option value={90}>Últimos 90 dias</option>
                        </select>
                    </div>

                    <div className="flex items-center gap-2">
                        <label className="text-sm font-medium text-gray-700">Métrica:</label>
                        <select
                            value={metric}
                            onChange={(e) => setMetric(e.target.value as typeof metric)}
                            className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        >
                            <option value="clicks">Cliques</option>
                            <option value="telegram_sends">Envios Telegram</option>
                            <option value="quality_score">Quality Score</option>
                        </select>
                    </div>

                    <button
                        onClick={loadAnalytics}
                        className="ml-auto bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
                    >
                        <span>🔄</span>
                        Atualizar
                    </button>
                </div>

                {/* Performance Cards */}
                {overview && <PerformanceCards data={overview} />}

                {/* Trends Chart */}
                <div className="mb-6">
                    <PerformanceChart trends={trends} period={period} />
                </div>

                {/* Top Products Table */}
                <div className="mb-6">
                    <TopProductsTable products={topProducts} metric={metric} />
                </div>

                {/* Store Comparison */}
                <div>
                    <StoreComparison stores={stores} />
                </div>
            </div>
        </div>
    );
}
