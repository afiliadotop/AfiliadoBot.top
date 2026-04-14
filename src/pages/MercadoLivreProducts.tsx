import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';
import { searchMLProducts, getTrendingMLProducts, MLProduct } from '../services/mercadolivre.service';
import { PageTransition } from '../components/layout/PageTransition';
import {
    Search, Loader2, AlertCircle, ShoppingCart, ExternalLink,
    Send, Package, Truck, ChevronDown, RefreshCw,
    TrendingUp, Filter, X
} from 'lucide-react';

// ==================== PRODUCT CARD ====================

const MLProductCard = ({ product, onSendTelegram, sending }: {
    product: MLProduct;
    onSendTelegram: (p: MLProduct) => void;
    sending: boolean;
}) => {
    const [imgError, setImgError] = useState(false);

    return (
        <article className="group relative bg-[#1c1c1e] border border-[#2a2a2d] rounded-2xl overflow-hidden flex flex-col hover:border-[#FFE600]/40 hover:shadow-xl hover:shadow-[#FFE600]/5 transition-all duration-300">
            {product.discount_percentage >= 5 && (
                <div className="absolute top-3 left-3 z-10 bg-[#FFE600] text-black text-[10px] font-black px-2 py-0.5 rounded-full uppercase tracking-wider shadow">
                    -{product.discount_percentage}%
                </div>
            )}
            {product.shipping_free && (
                <div className="absolute top-3 right-3 z-10 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-[9px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                    <Truck className="w-2.5 h-2.5" /> GRÁTIS
                </div>
            )}

            <div className="relative bg-white aspect-square overflow-hidden">
                {imgError ? (
                    <div className="w-full h-full flex items-center justify-center bg-[#2a2a2d]">
                        <Package className="w-10 h-10 text-slate-600" />
                    </div>
                ) : (
                    <img
                        src={product.image_url}
                        alt={product.name}
                        className="w-full h-full object-contain p-3 group-hover:scale-105 transition-transform duration-500"
                        onError={() => setImgError(true)}
                        loading="lazy"
                    />
                )}
            </div>

            <div className="flex flex-col gap-2 p-3 flex-1">
                <p className="text-xs text-slate-500 font-mono uppercase truncate">
                    🏪 {product.seller_name}
                </p>
                <h3 className="text-sm text-slate-200 font-medium leading-snug line-clamp-2 flex-1">
                    {product.name}
                </h3>

                {product.sold_quantity && product.sold_quantity > 100 ? (
                    <p className="text-[10px] text-slate-500 flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        {product.sold_quantity.toLocaleString('pt-BR')} vendidos
                    </p>
                ) : null}

                <div className="mt-auto">
                    {product.original_price && product.original_price > product.price && (
                        <p className="text-xs text-slate-500 line-through">
                            R$ {product.original_price.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </p>
                    )}
                    <p className="text-xl font-black text-[#FFE600]">
                        R$ {product.price.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </p>
                    {product.condition === 'used' && (
                        <span className="text-[9px] text-amber-500/80 font-mono bg-amber-500/10 border border-amber-500/20 px-1.5 py-0.5 rounded-full">
                            USADO
                        </span>
                    )}
                </div>

                <div className="flex gap-2 mt-2">
                    <a
                        href={product.affiliate_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 flex items-center justify-center gap-1.5 bg-[#FFE600] hover:bg-yellow-300 text-black font-black text-[10px] uppercase tracking-widest py-2.5 rounded-xl transition-colors"
                    >
                        <ExternalLink className="w-3 h-3" />
                        Ver no ML
                    </a>
                    <button
                        onClick={() => onSendTelegram(product)}
                        disabled={sending}
                        title="Enviar ao Telegram"
                        className="flex items-center justify-center gap-1 bg-blue-600/20 hover:bg-blue-600/40 border border-blue-600/30 hover:border-blue-500 text-blue-400 px-3 py-2 rounded-xl transition-all disabled:opacity-40"
                    >
                        <Send className={`w-3.5 h-3.5 ${sending ? 'animate-bounce' : ''}`} />
                    </button>
                </div>
            </div>
        </article>
    );
};

// ==================== SKELETON ====================

const ProductSkeleton = () => (
    <div className="bg-[#1c1c1e] border border-[#2a2a2d] rounded-2xl overflow-hidden animate-pulse">
        <div className="aspect-square bg-[#2a2a2d]" />
        <div className="p-3 space-y-2">
            <div className="h-2 bg-[#2a2a2d] rounded w-1/2" />
            <div className="h-3 bg-[#2a2a2d] rounded w-full" />
            <div className="h-3 bg-[#2a2a2d] rounded w-3/4" />
            <div className="h-6 bg-[#2a2a2d] rounded w-1/2 mt-2" />
            <div className="h-8 bg-[#2a2a2d] rounded-xl mt-2" />
        </div>
    </div>
);

// ==================== MAIN PAGE ====================

export const MercadoLivreProducts = () => {
    const { user } = useAuth();

    const [products, setProducts] = useState<MLProduct[]>([]);
    const [loading, setLoading] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [keyword, setKeyword] = useState('');
    const [inputValue, setInputValue] = useState('');
    const [sort, setSort] = useState<'relevance' | 'price_asc' | 'price_desc' | 'sales'>('relevance');
    const [condition, setCondition] = useState<'new' | 'used' | 'not_specified'>('new');
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(false);
    const [total, setTotal] = useState(0);
    const [sendingId, setSendingId] = useState<string | null>(null);
    const [toast, setToast] = useState<{ msg: string; type: 'ok' | 'err' } | null>(null);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const QUICK_SEARCHES = ['iPhone', 'Notebook', 'Airfryer', 'Fone Bluetooth', 'Smart TV', 'Tênis'];

    const showToast = (msg: string, type: 'ok' | 'err' = 'ok') => {
        setToast({ msg, type });
        setTimeout(() => setToast(null), 3500);
    };

    const fetchProducts = useCallback(async (kw: string, s: typeof sort, c: typeof condition, p: number, append = false) => {
        if (!kw.trim()) return;
        if (append) setLoadingMore(true);
        else { setLoading(true); setError(null); }

        try {
            // Chama ML API diretamente do browser (evita bloqueio 403 em IPs de servidores)
            const res = await searchMLProducts(kw, { sort: s, condition: c, page: p, limit: 20 });
            if (append) setProducts(prev => [...prev, ...res.products]);
            else setProducts(res.products);
            setHasMore(res.has_more);
            setTotal(res.total);
            setPage(res.page);
        } catch (err: any) {
            setError(err?.message || 'Erro ao buscar produtos');
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    }, []);

    // Debounce ao digitar
    useEffect(() => {
        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => {
            if (inputValue.trim()) {
                setKeyword(inputValue);
                fetchProducts(inputValue, sort, condition, 1, false);
            }
        }, 600);
        return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
    }, [inputValue]);

    // Refetch ao mudar filtros
    useEffect(() => {
        if (keyword) fetchProducts(keyword, sort, condition, 1, false);
    }, [sort, condition]);

    const handleLoadMore = () => { fetchProducts(keyword, sort, condition, page + 1, true); };

    const handleSendTelegram = async (product: MLProduct) => {
        setSendingId(product.id);
        try {
            await api.post('/mercadolivre/broadcast-telegram', {
                product_id: product.id,
                title: product.name,
                price: product.price,
                original_price: product.original_price,
                discount_percentage: product.discount_percentage,
                image_url: product.image_url,
                affiliate_link: product.affiliate_link,
                seller_name: product.seller_name,
                shipping_free: product.shipping_free,
                condition: product.condition,
            });
            showToast('✅ Enviado ao Telegram!');
        } catch {
            showToast('❌ Erro ao enviar ao Telegram', 'err');
        } finally {
            setSendingId(null);
        }
    };

    return (
        <PageTransition>
            <div className="min-h-screen bg-[#111113] pb-16">
                {/* Toast */}
                {toast && (
                    <div className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-xl text-sm font-medium shadow-2xl ${
                        toast.type === 'ok' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
                    }`}>
                        {toast.msg}
                    </div>
                )}

                {/* Hero Header */}
                <div className="bg-gradient-to-b from-[#1a1a00] to-[#111113] border-b border-[#FFE600]/10 px-6 py-10">
                    <div className="max-w-4xl mx-auto text-center">
                        <div className="flex items-center justify-center gap-3 mb-4">
                            <div className="w-10 h-10 bg-[#FFE600] rounded-xl flex items-center justify-center shadow-lg shadow-yellow-500/20">
                                <ShoppingCart className="w-5 h-5 text-black" />
                            </div>
                            <h1 className="text-3xl font-black text-white tracking-tight">Mercado Livre</h1>
                        </div>
                        <p className="text-slate-400 text-sm mb-8">
                            Busque produtos com links de afiliado gerados automaticamente
                        </p>

                        <div className="relative max-w-2xl mx-auto">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                            <input
                                id="ml-search"
                                name="ml-search"
                                type="text"
                                placeholder="Buscar produto no Mercado Livre..."
                                value={inputValue}
                                onChange={e => setInputValue(e.target.value)}
                                onKeyDown={e => {
                                    if (e.key === 'Enter' && inputValue.trim()) {
                                        setKeyword(inputValue);
                                        fetchProducts(inputValue, sort, condition, 1, false);
                                    }
                                }}
                                autoComplete="off"
                                className="w-full bg-[#1c1c1e] border-2 border-[#2a2a2d] focus:border-[#FFE600]/60 rounded-2xl py-4 pl-12 pr-14 text-white text-sm outline-none transition-all placeholder:text-slate-600 shadow-xl"
                            />
                            {inputValue && (
                                <button
                                    onClick={() => { setInputValue(''); setProducts([]); setKeyword(''); }}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            )}
                        </div>

                        <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
                            <span className="text-[10px] text-slate-600 uppercase tracking-wider font-mono">Tendências:</span>
                            {QUICK_SEARCHES.map(q => (
                                <button
                                    key={q}
                                    onClick={() => { setInputValue(q); setKeyword(q); fetchProducts(q, sort, condition, 1, false); }}
                                    className="text-[11px] px-3 py-1 rounded-full border border-[#2a2a2d] text-slate-400 hover:border-[#FFE600]/40 hover:text-[#FFE600] hover:bg-[#FFE600]/5 transition-all font-medium"
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Filtros */}
                <div className="sticky top-0 z-20 bg-[#111113]/95 backdrop-blur border-b border-[#2a2a2d] px-6 py-3">
                    <div className="max-w-7xl mx-auto flex items-center gap-3 flex-wrap">
                        <Filter className="w-4 h-4 text-slate-500 flex-shrink-0" />
                        <select
                            id="ml-sort"
                            value={sort}
                            onChange={e => setSort(e.target.value as typeof sort)}
                            className="bg-[#1c1c1e] border border-[#2a2a2d] text-slate-300 text-xs rounded-lg px-3 py-2 outline-none focus:border-[#FFE600]/40 cursor-pointer"
                        >
                            <option value="relevance">Relevância</option>
                            <option value="price_asc">Menor Preço</option>
                            <option value="price_desc">Maior Preço</option>
                            <option value="sales">Mais Vendidos</option>
                        </select>
                        <select
                            id="ml-condition"
                            value={condition}
                            onChange={e => setCondition(e.target.value as typeof condition)}
                            className="bg-[#1c1c1e] border border-[#2a2a2d] text-slate-300 text-xs rounded-lg px-3 py-2 outline-none focus:border-[#FFE600]/40 cursor-pointer"
                        >
                            <option value="new">Somente Novos</option>
                            <option value="used">Somente Usados</option>
                            <option value="not_specified">Todos</option>
                        </select>
                        {keyword && !loading && (
                            <span className="ml-auto text-xs text-slate-500 font-mono">
                                {total > 0 ? (
                                    <><span className="text-[#FFE600] font-bold">{products.length}</span> de {total.toLocaleString('pt-BR')} resultados</>
                                ) : 'Nenhum resultado'}
                            </span>
                        )}
                    </div>
                </div>

                {/* Conteúdo */}
                <div className="max-w-7xl mx-auto px-4 py-6">
                    {!keyword && !loading && (
                        <div className="flex flex-col items-center justify-center py-32 text-center">
                            <div className="w-20 h-20 bg-[#1c1c1e] rounded-3xl flex items-center justify-center mb-6 shadow-xl">
                                <ShoppingCart className="w-10 h-10 text-[#FFE600]/60" />
                            </div>
                            <h2 className="text-xl font-bold text-slate-300 mb-2">Busque qualquer produto</h2>
                            <p className="text-slate-500 text-sm max-w-sm">
                                Digite na barra acima e encontre produtos com links de afiliado gerados automaticamente
                            </p>
                        </div>
                    )}

                    {error && (
                        <div className="flex items-center gap-3 bg-red-950/30 border border-red-500/30 rounded-2xl p-5 mb-6">
                            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                            <div>
                                <p className="text-red-400 font-medium text-sm">Erro ao buscar produtos</p>
                                <p className="text-red-500/70 text-xs mt-0.5">{error}</p>
                            </div>
                            <button
                                onClick={() => fetchProducts(keyword, sort, condition, 1, false)}
                                className="ml-auto text-red-400 hover:text-red-300 text-xs flex items-center gap-1"
                            >
                                <RefreshCw className="w-3 h-3" /> Tentar novamente
                            </button>
                        </div>
                    )}

                    {loading && (
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
                            {Array.from({ length: 10 }).map((_, i) => <ProductSkeleton key={i} />)}
                        </div>
                    )}

                    {!loading && products.length > 0 && (
                        <>
                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
                                {products.map(product => (
                                    <MLProductCard
                                        key={product.id}
                                        product={product}
                                        onSendTelegram={handleSendTelegram}
                                        sending={sendingId === product.id}
                                    />
                                ))}
                            </div>
                            {hasMore && (
                                <div className="flex justify-center mt-10">
                                    <button
                                        onClick={handleLoadMore}
                                        disabled={loadingMore}
                                        className="flex items-center gap-2 bg-[#FFE600] hover:bg-yellow-300 disabled:bg-[#2a2a2d] text-black disabled:text-slate-500 font-black text-sm px-8 py-3.5 rounded-2xl transition-all shadow-lg shadow-yellow-500/10"
                                    >
                                        {loadingMore ? (
                                            <><Loader2 className="w-4 h-4 animate-spin" /> Carregando...</>
                                        ) : (
                                            <><ChevronDown className="w-4 h-4" /> Carregar mais</>
                                        )}
                                    </button>
                                </div>
                            )}
                        </>
                    )}

                    {!loading && keyword && products.length === 0 && !error && (
                        <div className="flex flex-col items-center justify-center py-32 text-center">
                            <Package className="w-14 h-14 text-slate-700 mb-4" />
                            <h2 className="text-lg font-bold text-slate-400 mb-2">Nenhum produto encontrado</h2>
                            <p className="text-slate-500 text-sm">Tente outro termo ou mude os filtros</p>
                        </div>
                    )}
                </div>
            </div>
        </PageTransition>
    );
};

export default MercadoLivreProducts;
