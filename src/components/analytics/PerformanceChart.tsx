import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { TrendData } from '../../services/analyticsService';

interface PerformanceChartProps {
    trends: TrendData[];
    period: number;
}

export default function PerformanceChart({ trends, period }: PerformanceChartProps) {
    // Format date for display
    const formattedData = trends.map((item) => ({
        ...item,
        displayDate: new Date(item.date).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
        }),
    }));

    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="mb-4">
                <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                    <span>📈</span>
                    Tendências de Cliques
                </h2>
                <p className="text-sm text-gray-600">
                    Evolução dos cliques nos últimos {period} dias
                </p>
            </div>

            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={formattedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis
                        dataKey="displayDate"
                        tick={{ fontSize: 12 }}
                        stroke="#6b7280"
                    />
                    <YAxis
                        tick={{ fontSize: 12 }}
                        stroke="#6b7280"
                        label={{ value: 'Cliques', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#6b7280' } }}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#fff',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                        }}
                        labelFormatter={(label) => `Data: ${label}`}
                        formatter={(value: number) => [`${value} cliques`, 'Total']}
                    />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey="clicks"
                        stroke="#4f46e5"
                        strokeWidth={3}
                        dot={{ fill: '#4f46e5', r: 4 }}
                        activeDot={{ r: 6 }}
                        name="Cliques"
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
