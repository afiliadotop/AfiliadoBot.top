import React, { useState, useEffect } from "react";
import { X, Save, Link as LinkIcon } from "lucide-react";
import { Product } from "../../hooks/useProducts";

interface ProductModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (product: Partial<Product>) => Promise<Product | null>;
    product?: Product | null;
}

export const ProductModal: React.FC<ProductModalProps> = ({ isOpen, onClose, onSave, product }) => {
    const [formData, setFormData] = useState({
        name: '',
        store: 'shopee',
        affiliate_link: '',
        current_price: '',
        original_price: '',
        discount_percentage: '',
        category: '',
        subcategory: '',
        image_url: '',
        description: '',
        stock_status: 'available',
        coupon_code: '',
        tags: '',
        is_active: true,
        is_featured: false
    });

    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (product) {
            setFormData({
                name: product.name || '',
                store: product.store || 'shopee',
                affiliate_link: product.affiliate_link || '',
                current_price: product.current_price?.toString() || '',
                original_price: product.original_price?.toString() || '',
                discount_percentage: product.discount_percentage?.toString() || '',
                category: product.category || '',
                subcategory: product.subcategory || '',
                image_url: product.image_url || '',
                description: product.description || '',
                stock_status: product.stock_status || 'available',
                coupon_code: product.coupon_code || '',
                tags: product.tags?.join(', ') || '',
                is_active: product.is_active ?? true,
                is_featured: product.is_featured ?? false
            });
        } else {
            // Reset for new product
            setFormData({
                name: '',
                store: 'shopee',
                affiliate_link: '',
                current_price: '',
                original_price: '',
                discount_percentage: '',
                category: '',
                subcategory: '',
                image_url: '',
                description: '',
                stock_status: 'available',
                coupon_code: '',
                tags: '',
                is_active: true,
                is_featured: false
            });
        }
    }, [product, isOpen]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);

        const productData: Partial<Product> = {
            name: formData.name,
            store: formData.store,
            affiliate_link: formData.affiliate_link,
            current_price: parseFloat(formData.current_price),
            original_price: formData.original_price ? parseFloat(formData.original_price) : undefined,
            discount_percentage: formData.discount_percentage ? parseInt(formData.discount_percentage) : undefined,
            category: formData.category || undefined,
            subcategory: formData.subcategory || undefined,
            image_url: formData.image_url || undefined,
            description: formData.description || undefined,
            stock_status: formData.stock_status,
            coupon_code: formData.coupon_code || undefined,
            tags: formData.tags ? formData.tags.split(',').map(t => t.trim()) : [],
            is_active: formData.is_active,
            is_featured: formData.is_featured
        };

        const result = await onSave(productData);
        setSaving(false);

        if (result) {
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl">
                {/* Header */}
                <div className="sticky top-0 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-6 py-4 flex items-center justify-between">
                    <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
                        {product ? 'Editar Produto' : 'Novo Produto'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Basic Info */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Informações Básicas</h3>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                Nome do Produto *
                            </label>
                            <input
                                type="text"
                                required
                                className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                    Loja *
                                </label>
                                <select
                                    required
                                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                    value={formData.store}
                                    onChange={(e) => setFormData({ ...formData, store: e.target.value })}
                                >
                                    <option value="shopee">Shopee</option>
                                    <option value="aliexpress">AliExpress</option>
                                    <option value="amazon">Amazon</option>
                                    <option value="mercado_livre">Mercado Livre</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                    Categoria
                                </label>
                                <input
                                    type="text"
                                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                    value={formData.category}
                                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                    placeholder="Ex: Eletrônicos"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                Link de Afiliado *
                            </label>
                            <div className="relative">
                                <LinkIcon className="absolute left-3 top-3 text-slate-400 w-5 h-5" />
                                <input
                                    type="url"
                                    required
                                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                    value={formData.affiliate_link}
                                    onChange={(e) => setFormData({ ...formData, affiliate_link: e.target.value })}
                                    placeholder="https://..."
                                />
                            </div>
                        </div>
                    </div>

                    {/* Pricing */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Preços</h3>

                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                    Preço Atual *
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    required
                                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                    value={formData.current_price}
                                    onChange={(e) => setFormData({ ...formData, current_price: e.target.value })}
                                    placeholder="0.00"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                    Preço Original
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                    value={formData.original_price}
                                    onChange={(e) => setFormData({ ...formData, original_price: e.target.value })}
                                    placeholder="0.00"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                    Desconto %
                                </label>
                                <input
                                    type="number"
                                    min="0"
                                    max="100"
                                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                    value={formData.discount_percentage}
                                    onChange={(e) => setFormData({ ...formData, discount_percentage: e.target.value })}
                                    placeholder="0"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Additional Info */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">Informações Adicionais</h3>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                URL da Imagem
                            </label>
                            <input
                                type="url"
                                className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                value={formData.image_url}
                                onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                                placeholder="https://..."
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                Descrição
                            </label>
                            <textarea
                                rows={3}
                                className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none resize-none"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                placeholder="Descrição do produto..."
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                    Cupom
                                </label>
                                <input
                                    type="text"
                                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none uppercase"
                                    value={formData.coupon_code}
                                    onChange={(e) => setFormData({ ...formData, coupon_code: e.target.value.toUpperCase() })}
                                    placeholder="CUPOM10"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                                    Tags
                                </label>
                                <input
                                    type="text"
                                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                                    value={formData.tags}
                                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                                    placeholder="tag1, tag2, tag3"
                                />
                            </div>
                        </div>

                        <div className="flex items-center gap-6">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                                    checked={formData.is_active}
                                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                />
                                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Produto Ativo</span>
                            </label>

                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    className="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                                    checked={formData.is_featured}
                                    onChange={(e) => setFormData({ ...formData, is_featured: e.target.checked })}
                                />
                                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Produto Destaque</span>
                            </label>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-4 border-t border-slate-200 dark:border-slate-800">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg font-medium hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={saving}
                            className="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-500 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {saving ? (
                                <>Salvando...</>
                            ) : (
                                <>
                                    <Save className="w-4 h-4" />
                                    Salvar Produto
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
