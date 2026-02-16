import { useState } from 'react';
import type { TopProduct } from '../../services/analyticsService';

interface TopProductsTableProps {
    products: TopProduct[];
    metric: 'clicks' | 'telegram_sends' | 'quality_score';
}

export default function TopProductsTable({ products, metric }: TopProductsTableProps) {
    const [sortBy, setSortBy] = useState<'clicks' | 'ctr' | 'quality_score'>('clicks');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

    const metricLabels = {
        clicks: 'Cliques',
        telegram_sends: 'Envios Telegram',
        quality_score: 'Quality Score',
    };

    // Sort products
    const sortedProducts = [...products].sort((a, b) => {
        const aVal = a[sortBy];
        const bVal = b[sortBy];
        return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
    });

    const handleSort = (column: typeof sortBy) => {
        if (sortBy === column) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(column);
            setSortOrder('desc');
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="mb-4">
                <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                    <span>🏆</span>
                    Top 10 Produtos - {metricLabels[metric]}
                </h2>
                <p className="text-sm text-gray-600">
                    Produtos com melhor performance por {metricLabels[metric].toLowerCase()}
                </p>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                                #
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                                Produto
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                                Loja
                            </th>
                            <th
                                className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                onClick={() => handleSort('clicks')}
                            >
                                Cliques {sortBy === 'clicks' && (sortOrder === 'desc' ? '↓' : '↑')}
                            </th>
                            <th
                                className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                onClick={() => handleSort('ctr')}
                            >
                                CTR {sortBy === 'ctr' && (sortOrder === 'desc' ? '↓' : '↑')}
                            </th>
                            <th
                                className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                                onClick={() => handleSort('quality_score')}
                            >
                                Quality {sortBy === 'quality_score' && (sortOrder === 'desc' ? '↓' : '↑')}
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                                Desconto
                            </th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                                Preço
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {sortedProducts.map((product, index) => (
                            <tr
                                key={product.id}
                                className="hover:bg-blue-50 transition-colors"
                            >
                                <td className="px-4 py-3 text-sm font-medium text-gray-900">
                                    {index + 1}
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-3">
                                        {product.image_url && (
                                            <img
                                                src={product.image_url}
                                                alt={product.name}
                                                className="w-12 h-12 object-cover rounded"
                                            />
                                        )}
                                        <div className="max-w-xs">
                                            <p className="text-sm font-medium text-gray-900 truncate">
                                                {product.name}
                                            </p>
                                            <a
                                                href={product.affiliate_link}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs text-indigo-600 hover:text-indigo-800"
                                            >
                                                Ver produto →
                                            </a>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-600 capitalize">
                                    {product.store}
                                </td>
                                <td className="px-4 py-3 text-sm font-semibold text-gray-900">
                                    {product.click_count}
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-900">
                                    <span className={`font-medium ${product.ctr >= 5 ? 'text-green-600' : product.ctr >= 3 ? 'text-amber-600' : 'text-red-600'}`}>
                                        {product.ctr.toFixed(2)}%
                                    </span>
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full ${product.quality_score >= 80
                                                        ? 'bg-green-500'
                                                        : product.quality_score >= 60
                                                            ? 'bg-amber-500'
                                                            : 'bg-red-500'
                                                    }`}
                                                style={{ width: `${product.quality_score}%` }}
                                            />
                                        </div>
                                        <span className="text-sm font-medium text-gray-700 w-8">
                                            {product.quality_score}
                                        </span>
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-900">
                                    {product.discount_percentage > 0 ? (
                                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                                            -{product.discount_percentage}%
                                        </span>
                                    ) : (
                                        <span className="text-gray-400">—</span>
                                    )}
                                </td>
                                <td className="px-4 py-3 text-sm font-medium text-gray-900">
                                    R$ {product.current_price.toFixed(2)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {products.length === 0 && (
                    <div className="text-center py-12">
                        <p className="text-gray-500">Nenhum produto encontrado</p>
                    </div>
                )}
            </div>
        </div>
    );
}
