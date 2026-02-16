import type { PerformanceOverview } from '../../services/analyticsService';

interface PerformanceCardsProps {
    data: PerformanceOverview;
}

export default function PerformanceCards({ data }: PerformanceCardsProps) {
    const cards = [
        {
            title: 'Total de Cliques',
            value: data.total_clicks.toLocaleString('pt-BR'),
            icon: '👆',
            color: 'from-blue-500 to-blue-600',
            description: `Últimos ${data.period_days} dias`,
        },
        {
            title: 'CTR Médio',
            value: `${data.avg_ctr.toFixed(2)}%`,
            icon: '📈',
            color: 'from-green-500 to-green-600',
            description: 'Click-Through Rate',
        },
        {
            title: 'Top Loja',
            value: data.best_store.toUpperCase(),
            icon: '🏪',
            color: 'from-purple-500 to-purple-600',
            description: 'Melhor performance',
        },
        {
            title: 'Qualidade Média',
            value: `${data.avg_quality_score.toFixed(1)}/100`,
            icon: '⭐',
            color: 'from-amber-500 to-amber-600',
            description: 'Score dos produtos',
        },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {cards.map((card, index) => (
                <div
                    key={index}
                    className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden"
                >
                    <div className={`bg-gradient-to-r ${card.color} p-4`}>
                        <div className="flex items-center justify-between text-white">
                            <span className="text-3xl">{card.icon}</span>
                            <div className="text-right">
                                <p className="text-sm opacity-90">{card.title}</p>
                                <p className="text-2xl font-bold mt-1">{card.value}</p>
                            </div>
                        </div>
                    </div>
                    <div className="p-3 bg-gray-50">
                        <p className="text-xs text-gray-600 text-center">{card.description}</p>
                    </div>
                </div>
            ))}
        </div>
    );
}
