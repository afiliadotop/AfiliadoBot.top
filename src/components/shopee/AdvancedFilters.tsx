import React from 'react';
import { ProductFilters } from '../services/shopee.service';
import { X, Filter } from 'lucide-react';

interface AdvancedFiltersProps {
    filters: ProductFilters;
    onFilterChange: (filters: ProductFilters) => void;
    onClear: () => void;
    onClose?: () => void;
}

export const AdvancedFilters: React.FC<AdvancedFiltersProps> = ({
    filters,
    onFilterChange,
    onClear,
    onClose
}) => {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                    <Filter className="w-5 h-5 text-orange-500" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Filtros Avançados
                    </h3>
                </div>
                {onClose && (
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Price Range */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Faixa de Preço (R$)
                    </label>
                    <div className="flex items-center space-x-2">
                        <input
                            type="number"
                            placeholder="Mín"
                            value={filters.priceMin || ''}
                            onChange={(e) => onFilterChange({
                                ...filters,
                                priceMin: parseFloat(e.target.value) || undefined
                            })}
                            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                focus:ring-2 focus:ring-orange-500 dark:bg-gray-700 dark:text-white"
                        />
                        <span className="text-gray-500">-</span>
                        <input
                            type="number"
                            placeholder="Máx"
                            value={filters.priceMax || ''}
                            onChange={(e) => onFilterChange({
                                ...filters,
                                priceMax: parseFloat(e.target.value) || undefined
                            })}
                            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                focus:ring-2 focus:ring-orange-500 dark:bg-gray-700 dark:text-white"
                        />
                    </div>
                </div>

                {/* Rating Filter */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Avaliação Mínima
                    </label>
                    <select
                        value={filters.minRating || ''}
                        onChange={(e) => onFilterChange({
                            ...filters,
                            minRating: parseFloat(e.target.value) || undefined
                        })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
              focus:ring-2 focus:ring-orange-500 dark:bg-gray-700 dark:text-white"
                    >
                        <option value="">Todas</option>
                        <option value="3.5">3.5+ ⭐</option>
                        <option value="4">4+ ⭐</option>
                        <option value="4.5">4.5+ ⭐</option>
                        <option value="4.8">4.8+ ⭐</option>
                        <option value="4.9">4.9+ ⭐</option>
                    </select>
                </div>

                {/* Sales Filter */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Vendas Mínimas
                    </label>
                    <input
                        type="number"
                        placeholder="Ex: 100"
                        value={filters.minSales || ''}
                        onChange={(e) => onFilterChange({
                            ...filters,
                            minSales: parseInt(e.target.value) || undefined
                        })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
              focus:ring-2 focus:ring-orange-500 dark:bg-gray-700 dark:text-white"
                    />
                </div>

                {/* Discount Filter */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Desconto Mínimo (%)
                    </label>
                    <input
                        type="number"
                        placeholder="Ex: 20"
                        min="0"
                        max="100"
                        value={filters.minDiscount || ''}
                        onChange={(e) => onFilterChange({
                            ...filters,
                            minDiscount: parseInt(e.target.value) || undefined
                        })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
              focus:ring-2 focus:ring-orange-500 dark:bg-gray-700 dark:text-white"
                    />
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                    onClick={onClear}
                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 
            hover:text-orange-600 dark:hover:text-orange-400 transition-colors"
                >
                    Limpar Filtros
                </button>

                <div className="text-sm text-gray-500 dark:text-gray-400">
                    {Object.values(filters).filter(v => v !== undefined).length} filtros ativos
                </div>
            </div>
        </div>
    );
};
