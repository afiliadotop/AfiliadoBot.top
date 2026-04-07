import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import {
    Search, RefreshCw, Store, Tag, Zap, Send,
    AlertCircle, CheckCircle, ExternalLink, ChevronRight,
    TrendingUp, Users, X
} from 'lucide-react';
import { cjService, CJLink, CJAdvertiser } from '../services/cj.service';

type Tab = 'links' | 'advertisers';

// ==================== LINK CARD ====================

const CJLinkCard: React.FC<{ link: CJLink; onBroadcast: (link: CJLink) => void }> = ({
    link, onBroadcast
}) => {
    const hasDiscount =
        link.sale_price != null &&
        link.original_price != null &&
        link.original_price > link.sale_price;

    const discountPct = hasDiscount
        ? Math.round(((link.original_price! - link.sale_price!) / link.original_price!) * 100)
        : null;

    const formatPrice = (p?: number) =>
        p != null ? `R$ ${p.toFixed(2).replace('.', ',')}` : null;

    return (
        <div className="group bg-slate-900 border-2 border-slate-800 rounded-sm hover:border-emerald-500/50 transition-all duration-200 flex flex-col">
            {/* Image */}
            <div className="relative h-36 bg-slate-800 overflow-hidden rounded-t-sm">
                {link.image_url ? (
                    <img
                        src={link.image_url}
                        alt={link.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                    />
                ) : (
                    <div className="flex items-center justify-center h-full">
                        <Tag className="w-10 h-10 text-slate-700" />
                    </div>
                )}
                {discountPct != null && (
                    <span className="absolute top-2 right-2 bg-red-600 text-white text-[10px] font-black px-2 py-0.5 rounded-sm">
                        -{discountPct}%
                    </span>
                )}
                {link.promotion_type && (
                    <span className="absolute top-2 left-2 bg-emerald-600/90 text-white text-[9px] font-black px-1.5 py-0.5 rounded-sm uppercase tracking-wider">
                        {link.promotion_type}
                    </span>
                )}
            </div>

            {/* Body */}
            <div className="flex flex-col gap-2 p-3 flex-1">
                <p className="text-white font-bold text-xs leading-snug line-clamp-2">{link.title}</p>

                {link.advertiser_name && (
                    <p className="text-slate-500 text-[10px] flex items-center gap-1">
                        <Store className="w-3 h-3 text-emerald-600" />
                        {link.advertiser_name}
                    </p>
                )}

                {/* Price */}
                <div className="flex items-baseline gap-2 mt-auto">
                    {link.sale_price != null && (
                        <span className="text-emerald-400 font-black text-sm">
                            {formatPrice(link.sale_price)}
                        </span>
                    )}
                    {hasDiscount && (
                        <span className="text-slate-600 text-[10px] line-through">
                            {formatPrice(link.original_price)}
                        </span>
                    )}
                </div>

                {/* Coupon */}
                {link.coupon_code && (
                    <div className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-sm px-2 py-1">
                        <Tag className="w-3 h-3 text-emerald-400" />
                        <span className="text-emerald-400 font-mono text-xs font-bold">{link.coupon_code}</span>
                    </div>
                )}
            </div>

            {/* Actions */}
            <div className="flex border-t-2 border-slate-800">
                <a
                    href={link.click_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-1.5 flex-1 py-2 text-[10px] font-bold text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
                >
                    <ExternalLink className="w-3 h-3" />
                    VER OFERTA
                </a>
                <div className="w-px bg-slate-800" />
                <button
                    onClick={() => onBroadcast(link)}
                    className="flex items-center justify-center gap-1.5 flex-1 py-2 text-[10px] font-bold text-emerald-500 hover:text-white hover:bg-emerald-600 transition-all"
                >
                    <Send className="w-3 h-3" />
                    TELEGRAM
                </button>
            </div>
        </div>
    );
};

// ==================== ADVERTISER CARD ====================

const CJAdvertiserCard: React.FC<{ advertiser: CJAdvertiser }> = ({ advertiser }) => {
    const mainTerm = advertiser.programTerms?.[0];

    return (
        <div className="bg-slate-900 border-2 border-slate-800 rounded-sm p-4 hover:border-emerald-500/40 transition-all space-y-3">
            <div className="flex items-start gap-3">
                {advertiser.logoUrl ? (
                    <img
                        src={advertiser.logoUrl}
                        alt={advertiser.name}
                        className="w-10 h-10 object-contain rounded bg-white p-1 flex-shrink-0"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                    />
                ) : (
                    <div className="w-10 h-10 bg-slate-800 rounded flex items-center justify-center flex-shrink-0">
                        <Store className="w-5 h-5 text-slate-600" />
                    </div>
                )}
                <div className="flex-1 min-w-0">
                    <p className="text-white font-bold text-sm truncate">{advertiser.name}</p>
                    {advertiser.primaryUrl && (
                        <a
                            href={advertiser.primaryUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-emerald-500 text-[10px] hover:underline truncate block"
                        >
                            {advertiser.primaryUrl.replace(/^https?:\/\//, '')}
                        </a>
                    )}
                </div>
                {advertiser.joined && (
                    <span className="flex-shrink-0 text-[9px] bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded-sm font-black uppercase">
                        ATIVO
                    </span>
                )}
            </div>

            <div className="flex flex-wrap gap-2">
                {advertiser.category && (
                    <span className="text-[10px] font-mono text-slate-500 border border-slate-700 px-1.5 py-0.5 rounded-sm">
                        {advertiser.category}
                    </span>
                )}
                {advertiser.country && (
                    <span className="text-[10px] font-mono text-slate-500 border border-slate-700 px-1.5 py-0.5 rounded-sm">
                        {advertiser.country}
                    </span>
                )}
            </div>

            {mainTerm && (
                <div className="bg-slate-800/60 rounded-sm p-2 space-y-1">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">{mainTerm.name || 'Termo Principal'}</p>
                    <div className="flex items-center gap-1.5">
                        <TrendingUp className="w-3 h-3 text-green-400" />
                        <span className="text-green-400 text-xs font-bold">
                            {mainTerm.commissionAmount
                                ? `${mainTerm.commissionAmount}% ${mainTerm.commissionType || ''}`
                                : mainTerm.commissionType || 'Ver termos'}
                        </span>
                    </div>
                    {mainTerm.paidOnSales && (
                        <p className="text-[10px] text-slate-600">Comissão paga em vendas</p>
                    )}
                </div>
            )}
        </div>
    );
};

// ==================== BROADCAST MODAL ====================

const BroadcastModal: React.FC<{
    link: CJLink;
    onClose: () => void;
    onConfirm: (link: CJLink) => Promise<void>;
    loading: boolean;
}> = ({ link, onClose, onConfirm, loading }) => (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
        <div className="bg-slate-900 border-2 border-emerald-500/50 rounded-sm w-full max-w-md shadow-2xl shadow-emerald-500/10">
            <div className="flex items-center justify-between p-4 border-b-2 border-slate-800">
                <div className="flex items-center gap-2">
                    <Send className="w-4 h-4 text-emerald-400" />
                    <span className="text-white font-black text-sm uppercase tracking-widest">ENVIAR AO TELEGRAM</span>
                </div>
                <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
                    <X className="w-4 h-4" />
                </button>
            </div>
            <div className="p-4 space-y-3">
                <p className="text-slate-400 text-xs">Confirme o disparo desta oferta CJ para o canal Telegram:</p>
                <div className="bg-slate-800 rounded-sm p-3 space-y-1 border border-slate-700">
                    <p className="text-white font-bold text-sm">{link.title}</p>
                    {link.advertiser_name && (
                        <p className="text-slate-500 text-xs flex items-center gap-1">
                            <Store className="w-3 h-3" /> {link.advertiser_name}
                        </p>
                    )}
                    {link.sale_price && (
                        <p className="text-emerald-400 font-bold text-sm">
                            R$ {link.sale_price.toFixed(2).replace('.', ',')}
                        </p>
                    )}
                    {link.coupon_code && (
                        <p className="text-yellow-400 font-mono text-xs">🎟️ {link.coupon_code}</p>
                    )}
                </div>
            </div>
            <div className="flex gap-0 border-t-2 border-slate-800">
                <button
                    onClick={onClose}
                    className="flex-1 py-3 text-xs font-bold text-slate-500 hover:text-white hover:bg-slate-800 transition-all"
                >
                    CANCELAR
                </button>
                <div className="w-px bg-slate-800" />
                <button
                    onClick={() => onConfirm(link)}
                    disabled={loading}
                    className="flex-1 py-3 text-xs font-black text-white bg-emerald-600 hover:bg-emerald-500 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                    {loading ? (
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                        <Send className="w-3.5 h-3.5" />
                    )}
                    CONFIRMAR DISPARO
                </button>
            </div>
        </div>
    </div>
);

// ==================== MAIN PAGE ====================

const CJProducts: React.FC = () => {
    const [activeTab, setActiveTab] = useState<Tab>('links');
    const [links, setLinks] = useState<CJLink[]>([]);
    const [advertisers, setAdvertisers] = useState<CJAdvertiser[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [configured, setConfigured] = useState<boolean | null>(null);
    const [keywords, setKeywords] = useState('');
    const [relationshipStatus, setRelationshipStatus] = useState('joined');
    const [broadcastTarget, setBroadcastTarget] = useState<CJLink | null>(null);
    const [broadcasting, setBroadcasting] = useState(false);
    const [totalLinks, setTotalLinks] = useState(0);
    const [filterAdvertiser, setFilterAdvertiser] = useState('');
    const [joinedAdvertisers, setJoinedAdvertisers] = useState<CJAdvertiser[]>([]);

    useEffect(() => {
        cjService.getStatus().then(s => setConfigured(s?.configured ?? false));
        // Prepare list of advertisers for filtering on mount
        cjService.getAdvertisers({ relationship_status: 'joined', page_size: 100 })
            .then(res => setJoinedAdvertisers(res?.items || []))
            .catch(() => {});
    }, []);

    const fetchLinks = useCallback(async (kw?: string, advId?: string) => {
        setLoading(true);
        setError(null);
        try {
            const res = await cjService.searchLinks({ 
                keywords: kw || keywords || undefined,
                advertiser_ids: advId !== undefined ? advId : (filterAdvertiser || undefined),
                page_size: 50 
            });
            setLinks(res?.items || []);
            setTotalLinks(res?.total || 0);
        } catch {
            setError('Erro ao buscar links CJ. Verifique as credenciais.');
        } finally {
            setLoading(false);
        }
    }, [keywords, filterAdvertiser]);

    const fetchAdvertisers = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await cjService.getAdvertisers({ relationship_status: relationshipStatus, page_size: 50 });
            setAdvertisers(res?.items || []);
        } catch {
            setError('Erro ao buscar anunciantes CJ.');
        } finally {
            setLoading(false);
        }
    }, [relationshipStatus]);

    useEffect(() => {
        if (activeTab === 'links') fetchLinks();
        if (activeTab === 'advertisers') fetchAdvertisers();
    }, [activeTab, fetchLinks, fetchAdvertisers]);

    const handleBroadcast = async (link: CJLink) => {
        setBroadcasting(true);
        try {
            await cjService.broadcast({
                title: link.title,
                description: link.description,
                click_url: link.click_url,
                image_url: link.image_url,
                advertiser_name: link.advertiser_name,
                coupon_code: link.coupon_code,
                sale_price: link.sale_price,
                original_price: link.original_price,
                currency: link.currency,
                promotion_type: link.promotion_type,
            });
            toast.success(`✅ Oferta "${link.title.slice(0, 40)}..." enviada ao Telegram!`);
            setBroadcastTarget(null);
        } catch {
            toast.error('Erro ao enviar para o Telegram.');
        } finally {
            setBroadcasting(false);
        }
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        fetchLinks(keywords, filterAdvertiser);
    };

    const tabs = [
        { key: 'links' as Tab, label: 'LINKS & PRODUTOS', icon: Tag },
        { key: 'advertisers' as Tab, label: 'ANUNCIANTES', icon: Users },
    ];

    return (
        <div className="min-h-screen bg-slate-950 p-6 font-mono">
            {/* Broadcast Modal */}
            {broadcastTarget && (
                <BroadcastModal
                    link={broadcastTarget}
                    onClose={() => setBroadcastTarget(null)}
                    onConfirm={handleBroadcast}
                    loading={broadcasting}
                />
            )}

            {/* Header */}
            <div className="mb-8 border-b-2 border-slate-800 pb-6">
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-2 h-8 bg-emerald-500" />
                    <h1 className="text-2xl font-black text-white uppercase tracking-widest">
                        CJ AFFILIATE
                    </h1>
                    <span className="text-xs font-mono text-slate-500 border border-slate-700 px-2 py-0.5 rounded-sm ml-2">
                        Company #{import.meta.env.VITE_CJ_COMPANY_ID || '7533850'}
                    </span>
                </div>
                <p className="text-slate-500 text-sm ml-5">
                    Commission Junction — Links, anunciantes e disparo direto para o Telegram
                </p>

                {/* Status badge */}
                <div className="mt-4">
                    {configured !== null && (
                        <div className={`inline-flex items-center gap-2 text-xs px-3 py-2 border rounded-sm ${
                            configured
                                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                                : 'bg-red-500/10 border-red-500/30 text-red-400'
                        }`}>
                            {configured ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                            {configured ? 'API CJ ativa e configurada' : 'API CJ não configurada — verifique CJ_API_TOKEN e CJ_COMPANY_ID no .env'}
                        </div>
                    )}
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-0 mb-8 border-b-2 border-slate-800">
                {tabs.map(({ key, label, icon: Icon }) => (
                    <button
                        key={key}
                        onClick={() => setActiveTab(key)}
                        className={`flex items-center gap-2 px-5 py-3 text-xs font-black tracking-widest uppercase border-b-2 -mb-0.5 transition-colors ${
                            activeTab === key
                                ? 'border-emerald-500 text-emerald-400'
                                : 'border-transparent text-slate-500 hover:text-slate-300'
                        }`}
                    >
                        <Icon className="w-4 h-4" />
                        {label}
                    </button>
                ))}
            </div>

            {/* Error */}
            {error && (
                <div className="mb-6 flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-sm text-sm">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                </div>
            )}

            {/* ====== LINKS TAB ====== */}
            {activeTab === 'links' && (
                <div>
                    {/* Search bar */}
                    <form onSubmit={handleSearch} className="flex gap-2 mb-6 flex-wrap">
                        {/* Store filter */}
                        <div className="relative flex-1 min-w-[200px] max-w-xs">
                            <Store className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                            <select
                                value={filterAdvertiser}
                                onChange={e => setFilterAdvertiser(e.target.value)}
                                className="w-full bg-slate-900 border-2 border-slate-800 text-white text-xs placeholder-slate-600 pl-9 pr-4 py-2.5 rounded-sm focus:outline-none focus:border-emerald-500/50 transition-colors appearance-none"
                            >
                                <option value="">🌐 Todas as Lojas</option>
                                {joinedAdvertisers.map(adv => (
                                    <option key={adv.id} value={adv.id}>{adv.name}</option>
                                ))}
                            </select>
                        </div>
                        
                        <div className="relative flex-1 min-w-[250px]">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                            <input
                                id="cj-search-input"
                                type="text"
                                value={keywords}
                                onChange={e => setKeywords(e.target.value)}
                                placeholder="Buscar por produto, marca, categoria..."
                                className="w-full bg-slate-900 border-2 border-slate-800 text-white text-xs placeholder-slate-600 pl-9 pr-4 py-2.5 rounded-sm focus:outline-none focus:border-emerald-500/50 transition-colors"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-black px-4 py-2 rounded-sm transition-all disabled:opacity-50"
                        >
                            <Search className="w-3.5 h-3.5" />
                            BUSCAR
                        </button>
                        <button
                            type="button"
                            onClick={() => fetchLinks()}
                            disabled={loading}
                            className="flex items-center gap-2 bg-slate-900 border border-slate-700 text-slate-400 hover:text-white text-xs px-4 py-2 rounded-sm transition-all"
                        >
                            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                            ATUALIZAR
                        </button>
                    </form>

                    {loading && (
                        <div className="text-slate-500 text-sm text-center py-12 animate-pulse flex items-center justify-center gap-2">
                            <Zap className="w-4 h-4 text-emerald-500" />
                            Buscando links na CJ...
                        </div>
                    )}

                    {!loading && links.length > 0 && (
                        <>
                            <p className="text-slate-600 text-xs mb-4 uppercase tracking-wider flex items-center gap-2">
                                <span className="text-emerald-500 font-bold">{links.length}</span>
                                LINK{links.length !== 1 ? 'S' : ''} ENCONTRADO{links.length !== 1 ? 'S' : ''}
                                {totalLinks > links.length && (
                                    <span className="text-slate-700">(de {totalLinks.toLocaleString('pt-BR')} totais)</span>
                                )}
                            </p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                {links.map((link, i) => (
                                    <CJLinkCard
                                        key={link.link_id || i}
                                        link={link}
                                        onBroadcast={l => setBroadcastTarget(l)}
                                    />
                                ))}
                            </div>
                        </>
                    )}

                    {!loading && links.length === 0 && !error && (
                        <div className="text-center py-16 text-slate-600">
                            <Tag className="w-12 h-12 mx-auto mb-3 opacity-20" />
                            <p className="text-sm text-slate-500">Nenhum link encontrado.</p>
                            <p className="text-xs mt-2">Tente buscar por produto, marca ou categoria.</p>
                            <button
                                onClick={() => fetchLinks()}
                                className="mt-4 text-xs text-emerald-500 hover:text-emerald-400 border border-emerald-500/30 px-4 py-2 rounded-sm transition-colors"
                            >
                                <ChevronRight className="w-3 h-3 inline mr-1" />
                                Carregar todos os links
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* ====== ADVERTISERS TAB ====== */}
            {activeTab === 'advertisers' && (
                <div>
                    <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
                        <div className="flex gap-2 flex-wrap">
                            {[
                                { key: 'joined', label: '✅ ATIVOS' },
                                { key: 'not-joined', label: '🔍 DISPONÍVEIS' },
                                { key: 'applied', label: '⏳ APLICADOS' },
                            ].map(({ key, label }) => (
                                <button
                                    key={key}
                                    onClick={() => setRelationshipStatus(key)}
                                    className={`text-xs font-black uppercase px-4 py-2 rounded-sm border transition-all ${
                                        relationshipStatus === key
                                            ? 'bg-emerald-600 border-emerald-600 text-white'
                                            : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500'
                                    }`}
                                >
                                    {label}
                                </button>
                            ))}
                        </div>
                        <button
                            onClick={fetchAdvertisers}
                            disabled={loading}
                            className="flex items-center gap-2 bg-slate-900 border border-slate-700 text-slate-400 hover:text-white text-xs px-4 py-2 rounded-sm transition-all"
                        >
                            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                            ATUALIZAR
                        </button>
                    </div>

                    {loading && (
                        <div className="text-slate-500 text-sm text-center py-12 animate-pulse">
                            Carregando anunciantes CJ...
                        </div>
                    )}

                    {!loading && advertisers.length > 0 && (
                        <>
                            <p className="text-slate-600 text-xs mb-4 uppercase tracking-wider">
                                <span className="text-emerald-500 font-bold">{advertisers.length}</span> ANUNCIANTE{advertisers.length !== 1 ? 'S' : ''}
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {advertisers.map((adv, i) => (
                                    <CJAdvertiserCard key={adv.id || i} advertiser={adv} />
                                ))}
                            </div>
                        </>
                    )}

                    {!loading && advertisers.length === 0 && !error && (
                        <div className="text-center py-12 text-slate-600">
                            <Store className="w-12 h-12 mx-auto mb-3 opacity-20" />
                            <p className="text-sm">Nenhum anunciante encontrado para "{relationshipStatus}".</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default CJProducts;
