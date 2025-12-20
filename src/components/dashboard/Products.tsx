import { useEffect, useState } from "react";
import { Search, Plus, Filter, Trash2 } from "lucide-react";
import { api } from "../../services/api";
import { Product } from "../../types";
import { toast } from "sonner";
import { Skeleton } from "../ui/Skeleton";
import { PageTransition } from "../layout/PageTransition";

export const Products = () => {
    const [subTab, setSubTab] = useState<'list' | 'add'>('list');
    const [searchTerm, setSearchTerm] = useState('');
    const [filters, setFilters] = useState({ store: '', category: '' });
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);

    // Fetch real products
    useEffect(() => {
        const loadProducts = async () => {
            setLoading(true);
            // Simulate slight delay for skeleton demo
            await new Promise(r => setTimeout(r, 800));

            const data = await api.get<Product[]>('/products?limit=50');
            if (data && Array.isArray(data)) {
                setProducts(data);
            } else {
                // Fallback Mock Data
                setProducts([
                    { id: 1, name: "Smartphone XYZ 128GB", store: "Shopee", category: "Eletrônicos", price: 999.90, discount: 15, active: true },
                    { id: 2, name: "Fone Bluetooth Pro", store: "AliExpress", category: "Áudio", price: 129.90, discount: 35, active: true },
                    { id: 3, name: "Kindle 11ª Geração", store: "Amazon", category: "Leitura", price: 499.00, discount: 0, active: true },
                ]);
            }
            setLoading(false);
        };
        if (subTab === 'list') loadProducts();
    }, [subTab]);

    const filteredProducts = products.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        (filters.store ? p.store === filters.store : true) &&
        (filters.category ? p.category === filters.category : true)
    );

    return (
        <PageTransition>
            <div className="space-y-6">
                <div className="flex gap-4 border-b border-slate-200 dark:border-slate-800 pb-1">
                    <button
                        onClick={() => setSubTab('list')}
                        className={`pb-3 px-2 font-medium text-sm transition-all border-b-2 ${subTab === 'list'
                                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                            }`}
                    >
                        <div className="flex items-center gap-2"><Search size={16} /> Buscar Produtos</div>
                    </button>
                    <button
                        onClick={() => setSubTab('add')}
                        className={`pb-3 px-2 font-medium text-sm transition-all border-b-2 ${subTab === 'add'
                                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                            }`}
                    >
                        <div className="flex items-center gap-2"><Plus size={16} /> Adicionar Manualmente</div>
                    </button>
                </div>

                {subTab === 'list' ? (
                    <div className="space-y-4">
                        {/* Filters */}
                        <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-wrap gap-4 items-center">
                            <div className="flex-1 min-w-[200px] relative">
                                <Search className="absolute left-3 top-2.5 text-slate-400 w-4 h-4" />
                                <input
                                    type="text"
                                    placeholder="Buscar por nome..."
                                    className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                            <select
                                className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                                value={filters.store}
                                onChange={(e) => setFilters({ ...filters, store: e.target.value })}
                            >
                                <option value="">Todas as Lojas</option>
                                <option value="Shopee">Shopee</option>
                                <option value="AliExpress">AliExpress</option>
                                <option value="Amazon">Amazon</option>
                                <option value="Mercado Livre">Mercado Livre</option>
                            </select>
                            <select
                                className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                                value={filters.category}
                                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                            >
                                <option value="">Todas as Categorias</option>
                                <option value="Eletrônicos">Eletrônicos</option>
                                <option value="Moda">Moda</option>
                                <option value="Áudio">Áudio</option>
                            </select>
                            <button className="flex items-center gap-2 px-4 py-2 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 rounded-lg text-sm font-medium hover:bg-indigo-100 dark:hover:bg-indigo-900/40">
                                <Filter size={16} /> Filtros
                            </button>
                        </div>

                        {/* Table */}
                        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                            {loading ? (
                                <div className="p-4 space-y-4">
                                    {[...Array(5)].map((_, i) => (
                                        <div key={i} className="flex gap-4">
                                            <Skeleton className="h-12 w-20" />
                                            <Skeleton className="h-12 flex-1" />
                                            <Skeleton className="h-12 w-32" />
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <table className="w-full text-left text-sm">
                                    <thead className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                                        <tr>
                                            <th className="px-6 py-4 font-semibold text-slate-900 dark:text-slate-200">ID</th>
                                            <th className="px-6 py-4 font-semibold text-slate-900 dark:text-slate-200">Produto</th>
                                            <th className="px-6 py-4 font-semibold text-slate-900 dark:text-slate-200">Loja</th>
                                            <th className="px-6 py-4 font-semibold text-slate-900 dark:text-slate-200">Categoria</th>
                                            <th className="px-6 py-4 font-semibold text-slate-900 dark:text-slate-200">Preço</th>
                                            <th className="px-6 py-4 font-semibold text-slate-900 dark:text-slate-200">Desconto</th>
                                            <th className="px-6 py-4 font-semibold text-slate-900 dark:text-slate-200 text-right">Ações</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                                        {filteredProducts.map((p) => (
                                            <tr key={p.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                                                <td className="px-6 py-4 text-slate-500">#{p.id.toString().substring(0, 8)}</td>
                                                <td className="px-6 py-4 font-medium text-slate-900 dark:text-slate-200">{p.name}</td>
                                                <td className="px-6 py-4">
                                                    <span className={`px-2 py-1 rounded text-xs font-medium ${p.store === 'Shopee' ? 'bg-orange-100 text-orange-700' :
                                                            p.store === 'Amazon' ? 'bg-yellow-100 text-yellow-700' :
                                                                'bg-blue-100 text-blue-700'
                                                        }`}>
                                                        {p.store}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-slate-600 dark:text-slate-400">{p.category || '-'}</td>
                                                <td className="px-6 py-4 font-mono">R$ {Number(p.price || p.current_price || 0).toFixed(2)}</td>
                                                <td className="px-6 py-4">
                                                    {(p.discount || p.discount_percentage || 0) > 0 ? (
                                                        <span className="text-green-600 font-bold bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded-full text-xs">
                                                            -{p.discount || p.discount_percentage}%
                                                        </span>
                                                    ) : <span className="text-slate-400">-</span>}
                                                </td>
                                                <td className="px-6 py-4 text-right">
                                                    <button
                                                        className="text-slate-400 hover:text-red-500 transition-colors p-2"
                                                        onClick={() => toast.error('Funcionalidade de exclusão em breve!')}
                                                    >
                                                        <Trash2 size={16} />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="text-center py-20 bg-white dark:bg-slate-900 rounded-xl border border-dashed border-slate-300">
                        <p className="text-slate-500">Formulário de adição sendo migrado...</p>
                        <button
                            onClick={() => setSubTab('list')}
                            className="mt-4 text-indigo-600 font-medium hover:underline"
                        >
                            Voltar para lista
                        </button>
                    </div>
                )}
            </div>
        </PageTransition>
    );
};
