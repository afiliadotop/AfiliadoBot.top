import { useState } from "react";
import { Search, Plus, Filter, Trash2, Edit } from "lucide-react";
import { Skeleton } from "../ui/Skeleton";
import { PageTransition } from "../layout/PageTransition";
import { useProducts, Product } from "../../hooks/useProducts";
import { ProductModal } from "./ProductModal";

export const Products = () => {
    const { products, loading, createProduct, updateProduct, deleteProduct } = useProducts();
    const [searchTerm, setSearchTerm] = useState('');
    const [storeFilter, setStoreFilter] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState<Product | null>(null);

    const filteredProducts = products.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        (storeFilter ? p.store === storeFilter : true) &&
        (categoryFilter ? p.category === categoryFilter : true)
    );

    const handleDelete = async (id: number, name: string) => {
        if (confirm(`Tem certeza que deseja deletar "${name}"?`)) {
            await deleteProduct(id);
        }
    };

    const handleOpenModal = (product?: Product) => {
        setEditingProduct(product || null);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingProduct(null);
    };

    const handleSave = async (productData: Partial<Product>) => {
        if (editingProduct) {
            return await updateProduct(editingProduct.id, productData);
        } else {
            return await createProduct(productData);
        }
    };

    return (
        <PageTransition>
            <div className="space-y-6">
                <div className="flex gap-4 border-b border-slate-200 dark:border-slate-800 pb-1">
                    <div className="pb-3 px-2 font-medium text-sm border-b-2 border-indigo-500 text-indigo-600 dark:text-indigo-400">
                        <div className="flex items-center gap-2"><Search size={16} /> Buscar Produtos</div>
                    </div>
                    <button
                        onClick={() => handleOpenModal()}
                        className="pb-3 px-2 font-medium text-sm border-b-2 border-transparent text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                    >
                        <div className="flex items-center gap-2"><Plus size={16} /> Adicionar Manualmente</div>
                    </button>
                </div>

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
                            value={storeFilter}
                            onChange={(e) => setStoreFilter(e.target.value)}
                        >
                            <option value="">Shopee</option>
                            <option value="shopee">Shopee</option>
                            <option value="aliexpress">AliExpress</option>
                            <option value="amazon">Amazon</option>
                            <option value="mercado_livre">Mercado Livre</option>
                        </select>
                        <select
                            className="px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                            value={categoryFilter}
                            onChange={(e) => setCategoryFilter(e.target.value)}
                        >
                            <option value="">Todas as Categorias</option>
                            <option value="Eletrônicos">Eletrônicos</option>
                            <option value="Moda">Moda</option>
                            <option value="Casa">Casa</option>
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
                        ) : filteredProducts.length === 0 ? (
                            <div className="text-center py-20">
                                <p className="text-slate-500">Nenhum produto encontrado</p>
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
                                                <span className={`px-2 py-1 rounded text-xs font-medium ${p.store === 'shopee' ? 'bg-orange-100 text-orange-700' :
                                                    p.store === 'amazon' ? 'bg-yellow-100 text-yellow-700' :
                                                        'bg-blue-100 text-blue-700'
                                                    }`}>
                                                    {p.store}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-slate-600 dark:text-slate-400">{p.category || '-'}</td>
                                            <td className="px-6 py-4 font-mono">R$ {p.current_price.toFixed(2)}</td>
                                            <td className="px-6 py-4">
                                                {(p.discount_percentage || 0) > 0 ? (
                                                    <span className="text-green-600 font-bold bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded-full text-xs">
                                                        -{p.discount_percentage}%
                                                    </span>
                                                ) : <span className="text-slate-400">-</span>}
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="flex gap-2 justify-end">
                                                    <button
                                                        onClick={() => handleOpenModal(p)}
                                                        className="text-slate-400 hover:text-indigo-500 transition-colors p-2"
                                                        title="Editar"
                                                    >
                                                        <Edit size={16} />
                                                    </button>
                                                    <button
                                                        className="text-slate-400 hover:text-red-500 transition-colors p-2"
                                                        onClick={() => handleDelete(p.id, p.name)}
                                                        title="Deletar"
                                                    >
                                                        <Trash2 size={16} />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            </div>

            <ProductModal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                onSave={handleSave}
                product={editingProduct}
            />
        </PageTransition>
    );
};
