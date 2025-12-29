import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import { shopeeService, ShopeeProduct, ProductFilters, PaginationInfo } from '../services/shopee.service';
import { ShopeeProductCard } from '../components/shopee/ShopeeProductCard';
import { ShopeeSearch } from '../components/shopee/ShopeeSearch';
import { AdvancedFilters } from '../components/shopee/AdvancedFilters';
import { PageTransition } from '../components/layout/PageTransition';
import { Loader2, AlertCircle, Filter, SlidersHorizontal, ArrowLeft, Home, LayoutDashboard, ChevronUp } from 'lucide-react';

export const ShopeeProducts = () => {
    const { user } = useAuth();
    const [products, setProducts] = useState<ShopeeProduct[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [keyword, setKeyword] = useState<string>("");
    const [sortBy, setSortBy] = useState<'commission' | 'sales' | 'price'>('commission');
    const [showFilters, setShowFilters] = useState(false);

    // NEW: Pagination state
    const [page, setPage] = useState(1);
    const [pagination, setPagination] = useState<PaginationInfo | null>(null);
    const [loadingMore, setLoadingMore] = useState(false);

    // NEW: Advanced filters
    const [filters, setFilters] = useState<ProductFilters>({});

    const isAdmin = user?.role === 'admin';

    // Scroll to top state
    const [showScrollTop, setShowScrollTop] = useState(false);

    useEffect(() => {
        loadProducts();
    }, [sortBy]);

    useEffect(() => {
        const handleScroll = () => {
            setShowScrollTop(window.scrollY > 400);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const loadProducts = async (append: boolean = false) => {
        if (append) setLoadingMore(true);
        else setLoading(true);
        setError(null);

        try {
            const currentPage = append ? page + 1 : 1;
            const response = await shopeeService.getProducts(
                { ...filters, keyword: keyword || undefined, sortBy },
                currentPage,
                20
            );

            if (response) {
                if (append) {
                    setProducts(prev => [...prev, ...response.products]);
                } else {
                    setProducts(response.products);
                }
                setPagination(response.pagination);
                setPage(currentPage);
            } else {
                setError("Erro ao carregar produtos");
            }
        } catch (err) {
            setError("Erro ao conectar com o servidor");
            console.error("Load products error:", err);
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    };

    const handleSearch = (searchKeyword: string) => {
        setKeyword(searchKeyword);
        setPage(1);
        loadProducts(false);
    };

    const handleFilterChange = (newFilters: ProductFilters) => {
        setFilters(newFilters);
        setPage(1);
        loadProducts(false);
    };

    const handleLoadMore = () => {
        loadProducts(true);
    };

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <PageTransition>
            <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
                <div className="max-w-7xl mx-auto space-y-8">
                    {/* Navigation Header */}
                    <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                        <div className="flex items-center gap-4">
                            <Link
                                to="/dashboard/overview"
                                className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors group"
                            >
                                <div className="p-2 rounded-lg bg-slate-800 group-hover:bg-slate-700 transition-colors">
                                    <ArrowLeft className="w-5 h-5" />
                                </div>
                                <span className="text-sm font-medium">Voltar ao Dashboard</span>
                            </Link>

                            {/* Breadcrumb */}
                            <div className="hidden md:flex items-center gap-2 text-sm text-slate-500">
                                <LayoutDashboard className="w-4 h-4" />
                                <span>/</span>
                                <span className="text-orange-400 font-medium">Produtos Shopee</span>
                            </div>
                        </div>

                        {/* User Info */}
                        {user && (
                            <div className="hidden sm:flex items-center gap-2 text-sm">
                                <div className="px-3 py-1 bg-slate-800 rounded-lg">
                                    <span className="text-slate-400">Olá, </span>
                                    <span className="text-slate-200 font-medium">{user.name}</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Header */}
                    <div className="text-center space-y-4">
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-400 to-orange-600 bg-clip-text text-transparent">
                            🛍️ Produtos Shopee
                        </h1>
                        <p className="text-slate-400">
                            {isAdmin
                                ? "Produtos com maior comissão - Dashboard Admin"
                                : "Melhores ofertas e descontos"}
                        </p>
                    </div>

                    {/* Search */}
                    <ShopeeSearch
                        onSearch={handleSearch}
                        initialValue={keyword}
                    />

                    {/* Filters */}
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => setShowFilters(!showFilters)}
                            className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg hover:bg-slate-800 transition-colors text-sm"
                        >
                            <SlidersHorizontal className="w-4 h-4" />
                            Filtros Avançados {showFilters ? '▲' : '▼'}
                        </button>

                        <div className="flex items-center gap-2">
                            <span className="text-sm text-slate-400">Ordenar por:</span>
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value as any)}
                                className="bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                            >
                                {isAdmin && (
                                    <option value="commission">💰 Maior Comissão</option>
                                )}
                                <option value="sales">📦 Mais Vendidos</option>
                                <option value="price">💵 Menor Preço</option>
                            </select>
                        </div>
                    </div>

                    {/* Advanced Filters Panel */}
                    {showFilters && (
                        <AdvancedFilters
                            filters={filters}
                            onFilterChange={handleFilterChange}
                            onClear={() => handleFilterChange({})}
                            onClose={() => setShowFilters(false)}
                        />
                    )}

                    {/* Results Count */}
                    {!loading && products.length > 0 && pagination && (
                        <div className="text-sm text-slate-400">
                            Exibindo {products.length} de {pagination.total} produtos
                            {keyword && ` para "${keyword}"`}
                        </div>
                    )}

                    {/* Loading State */}
                    {loading && (
                        <div className="flex items-center justify-center py-20">
                            <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
                        </div>
                    )}

                    {/* Error State */}
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 flex items-center gap-4">
                            <AlertCircle className="w-6 h-6 text-red-400" />
                            <div>
                                <h3 className="font-semibold text-red-400">Erro</h3>
                                <p className="text-sm text-red-300">{error}</p>
                            </div>
                        </div>
                    )}

                    {/* Products Grid */}
                    {!loading && !error && products.length > 0 && (
                        <>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {products.map((product) => (
                                    <ShopeeProductCard
                                        key={product.itemId}
                                        product={product}
                                        showCommission={isAdmin}
                                    />
                                ))}
                            </div>

                            {/* Load More Button */}
                            {pagination?.hasMore && (
                                <div className="flex justify-center pt-8">
                                    <button
                                        onClick={handleLoadMore}
                                        disabled={loadingMore}
                                        className="px-8 py-3 bg-gradient-to-r from-orange-500 to-orange-600 
                                            hover:from-orange-600 hover:to-orange-700 rounded-lg font-semibold
                                            transition-all shadow-lg hover:shadow-xl disabled:opacity-50 
                                            disabled:cursor-not-allowed flex items-center gap-2"
                                    >
                                        {loadingMore ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                Carregando...
                                            </>
                                        ) : (
                                            <>
                                                Carregar Mais
                                                <span className="text-sm opacity-75">
                                                    ({pagination.total - products.length} restantes)
                                                </span>
                                            </>
                                        )}
                                    </button>
                                </div>
                            )}
                        </>
                    )}

                    {/* Empty State */}
                    {!loading && !error && products.length === 0 && (
                        <div className="text-center py-20 space-y-4">
                            <div className="text-6xl">🔍</div>
                            <h3 className="text-xl font-semibold text-slate-300">
                                Nenhum produto encontrado
                            </h3>
                            <p className="text-slate-400">
                                {keyword
                                    ? `Tente buscar por outro termo`
                                    : `Use a busca para encontrar produtos`}
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {/* Scroll to Top Button */}
            <button
                onClick={scrollToTop}
                className={`fixed bottom-8 right-8 p-4 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 z-50 ${showScrollTop
                        ? 'opacity-100 translate-y-0'
                        : 'opacity-0 translate-y-16 pointer-events-none'
                    }`}
                aria-label="Voltar ao topo"
            >
                <ChevronUp className="w-6 h-6" />
            </button>
        </PageTransition>
    );
};
