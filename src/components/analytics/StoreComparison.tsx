import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell } from 'recharts';
import type { StorePerformance } from '../../services/analyticsService';

interface StoreComparisonProps {
    stores: StorePerformance[];
}

const COLORS = ['#4f46e5', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

export default function StoreComparison({ stores }: StoreComparisonProps) {
    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="mb-6">
                <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                    <span>🏪</span>
                    Comparativo de Lojas
                </h2>
                <p className="text-sm text-gray-600">
                    Performance e métricas por loja
                </p>
            </div>

            {/* Bar Chart */}
            <div className="mb-8">
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={stores}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                        <XAxis
                            dataKey="store"
                            tick={{ fontSize: 12 }}
                            stroke="#6b7280"
                        />
                        <YAxis
                            tick={{ fontSize: 12 }}
                            stroke="#6b7280"
                            label={{ value: 'Total de Cliques', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#6b7280' } }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#fff',
                                border: '1px solid #e5e7eb',
                                borderRadius: '8px',
                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                            }}
                        />
                        <Legend />
                        <Bar dataKey="total_clicks" name="Total de Cliques" radius={[8, 8, 0, 0]}>
                            {stores.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {stores.map((store, index) => (
                    <div
                        key={store.store}
                        className="border-2 border-gray-100 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="font-bold text-gray-800 capitalize text-lg">
                                {store.store}
                            </h3>
                            <div
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: COLORS[index % COLORS.length] }}
                            />
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Produtos:</span>
                                <span className="font-semibold text-gray-900">{store.product_count}</span>
                            </div>

                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Total Cliques:</span>
                                <span className="font-semibold text-gray-900">{store.total_clicks}</span>
                            </div>

                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Média/Produto:</span>
                                <span className="font-semibold text-gray-900">{store.avg_clicks_per_product}</span>
                            </div>

                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">CTR:</span>
                                <span className={`font-semibold ${store.ctr >= 5 ? 'text-green-600' :
                                        store.ctr >= 3 ? 'text-amber-600' :
                                            'text-red-600'
                                    }`}>
                                    {store.ctr.toFixed(2)}%
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {stores.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-gray-500">Nenhuma loja encontrada</p>
                </div>
            )}
        </div>
    );
}
