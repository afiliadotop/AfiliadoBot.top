import React, { useState } from "react";
import { Search, Plus, Filter, Trash2, Edit, Package, Send } from "lucide-react";
import { Skeleton } from "../ui/Skeleton";
import { PageTransition } from "../layout/PageTransition";
import { useProducts, Product } from "../../hooks/useProducts";
import { ProductModal } from "./ProductModal";
import { EmptyState } from "../ui/EmptyState";
import { api } from "../../services/api";
import { toast } from "sonner";

export const Products = () => {
    const { products, loading, createProduct, updateProduct, deleteProduct } = useProducts();
    const [searchTerm, setSearchTerm] = useState('');
    const [storeFilter, setStoreFilter] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState<Product | null>(null);

    // ML Modal state
    const [isMLModalOpen, setIsMLModalOpen] = useState(false);
    const [mlProductUrl, setMlProductUrl] = useState('');
    const [mlCategory, setMlCategory] = useState('Eletrônicos');
    const [mlLoading, setMlLoading] = useState(false);

    const filteredProducts = (products || []).filter(p => {
        if (!p || !p.name) return false;
        return (
            p.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
            (storeFilter ? p.store === storeFilter : true) &&
            (categoryFilter ? p.category === categoryFilter : true)
        );
    });

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

    const handleSendToTelegram = async (product: Product) => {
        if (!confirm(`Enviar "${product.name}" para o Telegram?`)) {
            return;
        }

        try {
            // First, get the Telegram channel chat_id from settings
            const settingsResponse = await api.get<{ settings?: { group_chat_id?: string } }>('/telegram/status');

            if (!settingsResponse?.settings?.group_chat_id) {
                toast.error('❌ Configure o Chat ID do Telegram primeiro em Configurações → Telegram');
                return;
            }

            const chat_id = settingsResponse.settings.group_chat_id;

            // Now send the product with chat_id
            const response = await api.post('/telegram/send', {
                product_id: product.id,
                chat_id: chat_id
            });

            if (response) {
                toast.success('✅ Produto enviado para o Telegram com sucesso!');
            }
        } catch (error: any) {
            // Error already handled by api service with toast
            console.error('Erro ao enviar para Telegram:', error);
        }
    };

    const handleAddMLProduct = async () => {
        if (!mlProductUrl.trim()) {
            alert('Por favor, cole a URL do produto ML');
            return;
        }

        setMlLoading(true);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:8000/api/products/add-ml-product', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    product_url: mlProductUrl,
                    category: mlCategory
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Erro ao adicionar produto');
            }

            alert(data.message || 'Produto adicionado com sucesso!');
            setIsMLModalOpen(false);
            setMlProductUrl('');

            // Refresh products
            window.location.reload();

        } catch (error: any) {
            alert(error.message || 'Erro ao adicionar produto ML');
        } finally {
            setMlLoading(false);
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
                    <button
                        onClick={() => setIsMLModalOpen(true)}
                        className="pb-3 px-2 font-medium text-sm border-b-2 border-transparent text-slate-500 hover:text-green-600 dark:hover:text-green-400 transition-colors"
                    >
                        <div className="flex items-center gap-2"><Package size={16} /> Adicionar ML</div>
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
                            <EmptyState
                                icon={Package}
                                title="Nenhum produto encontrado"
                                description={searchTerm || storeFilter || categoryFilter
                                    ? "Tente ajustar seus filtros de busca para encontrar produtos."
                                    : "Comece adicionando produtos manualmente ou importando via CSV."}
                                action={!searchTerm && !storeFilter && !categoryFilter ? {
                                    label: "Adicionar Primeiro Produto",
                                    onClick: () => handleOpenModal()
                                } : undefined}
                            />
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
                                            <td className="px-6 py-4 text-slate-500">#{p?.id?.toString().substring(0, 8) || '---'}</td>
                                            <td className="px-6 py-4 font-medium text-slate-900 dark:text-slate-200">{p?.name || 'Sem nome'}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 py-1 rounded text-xs font-medium ${p?.store === 'shopee' ? 'bg-orange-100 text-orange-700' :
                                                    p?.store === 'amazon' ? 'bg-yellow-100 text-yellow-700' :
                                                        'bg-blue-100 text-blue-700'
                                                    }`}>
                                                    {p?.store || 'Desconhecida'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-slate-600 dark:text-slate-400">{p?.category || '-'}</td>
                                            <td className="px-6 py-4 font-mono">R$ {(p.current_price || 0).toFixed(2)}</td>
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
                                                        onClick={() => handleSendToTelegram(p)}
                                                        className="text-blue-600 hover:text-blue-500 transition-colors"
                                                        title="Enviar para Telegram"
                                                        aria-label={`Enviar ${p?.name || 'produto'} para Telegram`}
                                                    >
                                                        <Send size={16} />
                                                    </button>
                                                    <button
                                                        onClick={() => handleOpenModal(p)}
                                                        className="text-indigo-600 hover:text-indigo-500 transition-colors"
                                                        aria-label={`Editar produto ${p?.name || 'sem nome'}`}
                                                    >
                                                        <Edit size={16} />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDelete(p.id, p.name)}
                                                        className="text-red-600 hover:text-red-500 transition-colors"
                                                        aria-label={`Deletar produto ${p?.name || 'sem nome'}`}
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

            {/* ML Modal */}
            {isMLModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-slate-900 rounded-xl p-6 w-full max-w-md mx-4 border border-slate-200 dark:border-slate-800">
                        <h3 className="text-xl font-semibold mb-4 text-slate-900 dark:text-slate-100">
                            Adicionar Produto Mercado Livre
                        </h3>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2 text-slate-700 dark:text-slate-300">
                                    URL do Produto
                                </label>
                                <input
                                    type="text"
                                    placeholder="https://produto.mercadolivre.com.br/MLB-123456"
                                    className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                                    value={mlProductUrl}
                                    onChange={(e) => setMlProductUrl(e.target.value)}
                                />
                                <p className="text-xs text-slate-500 mt-1">Cole a URL completa do produto do Mercado Livre</p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2 text-slate-700 dark:text-slate-300">
                                    Categoria
                                </label>
                                <select
                                    className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                                    value={mlCategory}
                                    onChange={(e) => setMlCategory(e.target.value)}
                                >
                                    <option>Eletrônicos</option>
                                    <option>Celulares</option>
                                    <option>Informática</option>
                                    <option>Casa e Jardim</option>
                                    <option>Esportes</option>
                                    <option>Moda</option>
                                    <option>Áudio</option>
                                </select>
                            </div>
                        </div>

                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={handleAddMLProduct}
                                disabled={mlLoading}
                                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {mlLoading ? 'Adicionando...' : '✅ Adicionar'}
                            </button>
                            <button
                                onClick={() => {
                                    setIsMLModalOpen(false);
                                    setMlProductUrl('');
                                }}
                                disabled={mlLoading}
                                className="px-6 bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium py-2 rounded-lg transition-colors disabled:opacity-50"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </PageTransition>
    );
};
