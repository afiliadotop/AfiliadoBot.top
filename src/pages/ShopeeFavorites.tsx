import React, { useState, useEffect } from 'react';
import { shopeeService, FavoriteProduct } from '../services/shopee.service';
import { ShopeeProductCard } from '../components/shopee/ShopeeProductCard';
import { PageTransition } from '../components/layout/PageTransition';
import { Loader2, Heart, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';

export const ShopeeFavorites = () => {
    const [favorites, setFavorites] = useState<FavoriteProduct[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadFavorites();
    }, []);

    const loadFavorites = async () => {
        setLoading(true);
        try {
            const response = await shopeeService.getFavorites();
            if (response) {
                setFavorites(response.favorites);
            }
        } catch (error) {
            toast.error('Erro ao carregar favoritos');
        } finally {
            setLoading(false);
        }
    };

    const handleFavoriteRemoved = (itemId: number) => {
        setFavorites(prev => prev.filter(f => f.itemId !== itemId));
        toast.success('Removido dos favoritos');
    };

    return (
        <PageTransition>
            <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
                <div className="max-w-7xl mx-auto space-y-8">
                    {/* Header */}
                    <div className="text-center space-y-4">
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-red-400 to-pink-600 bg-clip-text text-transparent">
                            ❤️ Meus Favoritos
                        </h1>
                        <p className="text-slate-400">
                            {loading ? 'Carregando...' : `${favorites.length} produtos salvos`}
                        </p>
                    </div>

                    {/* Loading State */}
                    {loading && (
                        <div className="flex items-center justify-center py-20">
                            <Loader2 className="w-8 h-8 animate-spin text-red-500" />
                        </div>
                    )}

                    {/* Empty State */}
                    {!loading && favorites.length === 0 && (
                        <div className="text-center py-20 space-y-6">
                            <div className="text-8xl mb-4">💔</div>
                            <h3 className="text-2xl font-semibold text-slate-300">
                                Nenhum favorito ainda
                            </h3>
                            <p className="text-slate-400 max-w-md mx-auto">
                                Adicione produtos aos favoritos clicando no ícone ❤️ nos cards de produtos
                            </p>
                            <a
                                href="/shopee"
                                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 
                  hover:from-orange-600 hover:to-orange-700 rounded-lg font-semibold transition-all"
                            >
                                <ShoppingBag className="w-5 h-5" />
                                Explorar Produtos
                            </a>
                        </div>
                    )}

                    {/* Favorites Grid */}
                    {!loading && favorites.length > 0 && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {favorites.map((product) => (
                                <div key={product.itemId} className="relative">
                                    <ShopeeProductCard
                                        product={product}
                                        showCommission={false}
                                    />
                                    <div className="mt-2 text-xs text-slate-500 text-center">
                                        Adicionado em {new Date(product.favoritedAt).toLocaleDateString('pt-BR')}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </PageTransition>
    );
};
