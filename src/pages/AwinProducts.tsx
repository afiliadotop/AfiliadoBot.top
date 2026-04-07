import React, { useState, useEffect, useCallback } from 'react';
import { awinService, AwinOffer, AwinProgram, AwinPerformanceEntry } from '../services/awin.service';
import { AwinOfferCard } from '../components/awin/AwinOfferCard';
import {
    Tag, TrendingUp, Zap, RefreshCw, Store, BarChart2,
    AlertCircle, CheckCircle, ChevronDown
} from 'lucide-react';

type Tab = 'offers' | 'programs' | 'performance';

const AwinProducts: React.FC = () => {
    const [activeTab, setActiveTab] = useState<Tab>('offers');

    const [offers, setOffers] = useState<AwinOffer[]>([]);
    const [programs, setPrograms] = useState<AwinProgram[]>([]);
    const [performance, setPerformance] = useState<AwinPerformanceEntry[]>([]);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [configured, setConfigured] = useState<boolean | null>(null);
    const [quota, setQuota] = useState<{ current: number; max: number } | null>(null);

    const [offerType, setOfferType] = useState<string>('all');
    const [programRelationship, setProgramRelationship] = useState<string>('joined');
    const [onlyJoined, setOnlyJoined] = useState(true);
    const [isHot, setIsHot] = useState(false);

    // --- Filter logic ---
    const filteredOffers = offers.filter(offer => {
        if (onlyJoined && offer.advertiser?.joined !== true) return false;
        if (isHot) {
            const typeKey = offer.type || offer.promotion_type || 'deal';
            if (typeKey !== 'voucher' && typeKey !== 'deal') return false;
        }
        return true;
    });

    // --- Check config & Quota ---
    useEffect(() => {
        awinService.getStatus().then(status => {
            setConfigured(status?.configured ?? false);
        });
        awinService.getQuota().then(res => {
            if (res && res.current !== undefined) setQuota(res);
            else if (res && res.quota && res.quota.current !== undefined) setQuota(res.quota);
        }).catch(() => console.error("Could not fetch Awin Quota"));
    }, []);

    // --- Fetch Offers ---
    const fetchOffers = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const types = offerType === 'all' ? undefined : [offerType];
            const result = await awinService.getOffers({ promotion_types: types, page_size: 50 });
            // The JSON from Awin is { "data": [...], "pagination": {...} }
            const list = result?.data || result?.offers || (Array.isArray(result) ? result : []);
            setOffers(list);
        } catch {
            setError('Erro ao buscar ofertas. Verifique as credenciais Awin.');
        } finally {
            setLoading(false);
        }
    }, [offerType]);

    // --- Fetch Programs ---
    const fetchPrograms = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await awinService.getPrograms(programRelationship);
            setPrograms(result?.programs || []);
        } catch {
            setError('Erro ao buscar programas.');
        } finally {
            setLoading(false);
        }
    }, [programRelationship]);

    // --- Fetch Performance ---
    const fetchPerformance = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const now = new Date();
            const start = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
            const end = now.toISOString().split('T')[0];
            const result = await awinService.getPerformanceReport({ start_date: start, end_date: end, region: 'BR' });
            setPerformance(result?.data || []);
        } catch {
            setError('Erro ao buscar performance.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (activeTab === 'offers') fetchOffers();
        if (activeTab === 'programs') fetchPrograms();
        if (activeTab === 'performance') fetchPerformance();
    }, [activeTab, fetchOffers, fetchPrograms, fetchPerformance]);

    const tabs: { key: Tab; label: string; icon: any }[] = [
        { key: 'offers', label: 'PROMOÇÕES & CUPONS', icon: Tag },
        { key: 'programs', label: 'PROGRAMAS', icon: Store },
        { key: 'performance', label: 'PERFORMANCE', icon: BarChart2 },
    ];

    return (
        <div className="min-h-screen bg-slate-950 p-6 font-mono">
            {/* Header */}
            <div className="mb-8 border-b-2 border-slate-800 pb-6">
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-2 h-8 bg-orange-500"></div>
                    <h1 className="text-2xl font-black text-white uppercase tracking-widest">
                        AWIN AFFILIATE
                    </h1>
                    <span className="text-xs font-mono text-slate-500 border border-slate-700 px-2 py-0.5 rounded-sm ml-2">
                        Publisher #{import.meta.env.VITE_AWIN_PUBLISHER_ID || '1302821'}
                    </span>
                </div>
                <p className="text-slate-500 text-sm ml-5">
                    Gestão de programas afiliados, cupons, ofertas e relatórios de performance
                </p>

                {/* Status & Quota */}
                <div className="mt-4 flex flex-wrap items-center gap-4">
                    {configured !== null && (
                        <div className={`flex items-center gap-2 text-xs px-3 py-2 border rounded-sm w-fit ${
                            configured
                                ? 'bg-green-500/10 border-green-500/30 text-green-400'
                                : 'bg-red-500/10 border-red-500/30 text-red-400'
                        }`}>
                            {configured ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                            {configured ? 'API Awin ativa e respondendo' : 'API Awin não configurada — verifique o .env'}
                        </div>
                    )}
                    {quota && (
                        <div className="flex items-center gap-2 text-xs px-3 py-2 border border-slate-700 bg-slate-900 rounded-sm text-slate-400">
                            <Zap className="w-3.5 h-3.5 text-orange-400" />
                            Quota da API Awin (Uso Hoje): 
                            <span className={`font-bold ${quota.current >= quota.max * 0.8 ? 'text-red-400' : 'text-white'}`}>
                                {quota.current} / {quota.max}
                            </span>
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
                                ? 'border-orange-500 text-orange-400'
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

            {/* ====== OFFERS TAB ====== */}
            {activeTab === 'offers' && (
                <div>
                        {/* Filters */}
                        <div className="flex flex-col gap-4 mb-6">
                            <div className="flex items-center gap-3 flex-wrap">
                                {['all', 'voucher', 'deal', 'product'].map(type => (
                                    <button
                                        key={type}
                                        onClick={() => setOfferType(type)}
                                        className={`text-xs font-black uppercase px-4 py-2 rounded-sm border transition-all ${
                                            offerType === type
                                                ? 'bg-orange-600 border-orange-600 text-white'
                                                : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500'
                                        }`}
                                    >
                                        {type === 'all' ? '🔥 TODOS' : type === 'voucher' ? '🎟️ CUPONS' : type === 'deal' ? '💥 DEALS' : '📦 PRODUTOS'}
                                    </button>
                                ))}
                                
                                {/* Botão Imperdíveis */}
                                <button
                                    onClick={() => setIsHot(!isHot)}
                                    className={`text-xs font-black uppercase px-4 py-2 rounded-sm border transition-all ${
                                        isHot
                                            ? 'bg-yellow-500 border-yellow-500 text-slate-900 shadow-[0_0_15px_rgba(234,179,8,0.3)]'
                                            : 'bg-slate-900 border-slate-700 text-yellow-500 hover:border-yellow-600'
                                    }`}
                                    title="Mostra apenas Cupons ou Ofertas Especiais"
                                >
                                    ⭐ IMPERDÍVEIS
                                </button>

                                <button
                                    onClick={fetchOffers}
                                    disabled={loading}
                                    className="ml-auto flex items-center gap-2 bg-slate-900 border border-slate-700 text-slate-400 hover:text-white text-xs px-4 py-2 rounded-sm transition-all"
                                >
                                    <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                                    ATUALIZAR
                                </button>
                            </div>
                            
                            {/* Toggle Programas Participo */}
                            <div className="flex items-center gap-2 mt-1">
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <div className={`w-4 h-4 rounded-sm border flex items-center justify-center transition-colors ${
                                        onlyJoined ? 'bg-orange-500 border-orange-500' : 'bg-slate-900 border-slate-600 group-hover:border-orange-500'
                                    }`}>
                                        {onlyJoined && <CheckCircle className="w-3 h-3 text-white" />}
                                    </div>
                                    <input 
                                        type="checkbox" 
                                        className="hidden" 
                                        checked={onlyJoined} 
                                        onChange={() => setOnlyJoined(!onlyJoined)} 
                                    />
                                    <span className="text-sm text-slate-400 group-hover:text-white transition-colors">
                                        Focar apenas em programas que <strong className="text-orange-400">já participo</strong>
                                    </span>
                                </label>
                            </div>
                        </div>

                        {/* Loading */}
                        {loading && (
                            <div className="text-slate-500 text-sm text-center py-12 animate-pulse">
                                Carregando ofertas da Awin...
                            </div>
                        )}

                        {/* Grid de Ofertas */}
                        {!loading && filteredOffers.length > 0 && (
                            <>
                                <p className="text-slate-600 text-xs mb-4 uppercase tracking-wider flex items-center gap-2">
                                    <span className="text-orange-500 font-bold">{filteredOffers.length}</span> OFERTA{filteredOffers.length !== 1 ? 'S' : ''} ENCONTRADA{filteredOffers.length !== 1 ? 'S' : ''}
                                    {offers.length > filteredOffers.length && (
                                        <span className="text-slate-700"> (de {offers.length} totais)</span>
                                    )}
                                </p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                    {filteredOffers.map((offer, i) => (
                                        <AwinOfferCard key={offer.awin_offer_id || offer.promotionId || i} offer={offer} />
                                    ))}
                                </div>
                            </>
                        )}

                        {!loading && filteredOffers.length === 0 && !error && (
                            <div className="text-center py-12 text-slate-600">
                                <Tag className="w-12 h-12 mx-auto mb-3 opacity-30" />
                                <p className="text-sm">Nenhuma oferta encontrada com os filtros atuais.</p>
                                {(onlyJoined || isHot) && (
                                    <button 
                                        onClick={() => { setOnlyJoined(false); setIsHot(false); setOfferType('all'); }} 
                                        className="mt-4 text-xs text-orange-500 hover:text-orange-400 border border-orange-500/30 px-4 py-2 rounded-sm"
                                    >
                                        Limpar Filtros
                                    </button>
                                )}
                                <p className="text-xs mt-4 text-slate-700">Verifique os programas ativos na aba PROGRAMAS.</p>
                            </div>
                        )}
                </div>
            )}

            {/* ====== PROGRAMS TAB ====== */}
            {activeTab === 'programs' && (
                <div>
                    <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
                        <div className="flex gap-2">
                            {['joined', 'pending', 'notjoined'].map(rel => (
                                <button
                                    key={rel}
                                    onClick={() => setProgramRelationship(rel)}
                                    className={`text-xs font-black uppercase px-4 py-2 rounded-sm border transition-all ${
                                        programRelationship === rel
                                            ? 'bg-orange-600 border-orange-600 text-white'
                                            : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500'
                                    }`}
                                >
                                    {rel === 'joined' ? '✅ ATIVOS' : rel === 'pending' ? '⏳ PENDENTES' : '🔍 DISPONÍVEIS'}
                                </button>
                            ))}
                        </div>
                        <button
                            onClick={fetchPrograms}
                            disabled={loading}
                            className="flex items-center gap-2 bg-slate-900 border border-slate-700 text-slate-400 hover:text-white text-xs px-4 py-2 rounded-sm transition-all"
                        >
                            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                            ATUALIZAR
                        </button>
                    </div>

                    {loading && <div className="text-slate-500 text-sm text-center py-12 animate-pulse">Carregando programas...</div>}

                    {!loading && programs.length > 0 && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {programs.map((prog, i) => (
                                <div key={prog.id || i} className="bg-slate-900 border-2 border-slate-800 rounded-sm p-4 hover:border-orange-500/50 transition-all space-y-2">
                                    <div className="flex items-center gap-2">
                                        <Store className="w-4 h-4 text-orange-500" />
                                        <span className="text-white font-bold text-sm truncate">
                                            {prog.displayName || prog.name || `Programa #${prog.id}`}
                                        </span>
                                    </div>
                                    {prog.primaryRegion?.countryCode && (
                                        <span className="text-[10px] font-mono text-slate-500 border border-slate-700 px-1.5 py-0.5 rounded-sm">
                                            {prog.primaryRegion.countryCode}
                                        </span>
                                    )}
                                    {prog.commissionRate != null && (
                                        <div className="flex items-center gap-1.5 text-green-400 text-xs font-bold">
                                            <TrendingUp className="w-3.5 h-3.5" />
                                            {prog.commissionRate}% Comissão
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {!loading && programs.length === 0 && !error && (
                        <div className="text-center py-12 text-slate-600">
                            <Store className="w-12 h-12 mx-auto mb-3 opacity-30" />
                            <p className="text-sm">Nenhum programa encontrado para "{programRelationship}".</p>
                        </div>
                    )}
                </div>
            )}

            {/* ====== PERFORMANCE TAB ====== */}
            {activeTab === 'performance' && (
                <div>
                    <div className="flex items-center gap-2 mb-6 text-slate-500 text-xs">
                        <BarChart2 className="w-4 h-4" />
                        <span>PERFORMANCE DO MÊS ATUAL — Região: BR / America/Sao_Paulo</span>
                        <button
                            onClick={fetchPerformance}
                            disabled={loading}
                            className="ml-auto flex items-center gap-1.5 bg-slate-900 border border-slate-700 text-slate-400 hover:text-white px-3 py-1.5 rounded-sm transition-all"
                        >
                            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                            ATUALIZAR
                        </button>
                    </div>

                    {loading && <div className="text-slate-500 text-sm text-center py-12 animate-pulse">Carregando performance...</div>}

                    {!loading && performance.length > 0 && (
                        <>
                            {/* Summary Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                                <div className="bg-slate-900 border border-slate-800 rounded p-4 flex flex-col gap-2">
                                    <span className="text-slate-500 text-[10px] font-bold tracking-widest uppercase">Cliques Totais</span>
                                    <span className="text-2xl text-white font-black">
                                        {performance.reduce((acc, row) => acc + (row.clicks || 0), 0).toLocaleString('pt-BR')}
                                    </span>
                                </div>
                                <div className="bg-slate-900 border border-slate-800 rounded p-4 flex flex-col gap-2">
                                    <span className="text-slate-500 text-[10px] font-bold tracking-widest uppercase">Vendas / Transações</span>
                                    <span className="text-2xl text-blue-400 font-black">
                                        {performance.reduce((acc, row) => acc + (row.transactions || 0), 0).toLocaleString('pt-BR')}
                                    </span>
                                </div>
                                <div className="bg-slate-900 border-2 border-orange-500/20 rounded p-4 flex flex-col gap-2">
                                    <span className="text-slate-500 text-[10px] font-bold tracking-widest uppercase">Comissão Acumulada</span>
                                    <span className="text-2xl text-green-400 font-black">
                                        R$ {performance.reduce((acc, row) => acc + (row.commissions || 0), 0).toFixed(2).replace('.', ',')}
                                    </span>
                                </div>
                                <div className="bg-slate-900 border border-slate-800 rounded p-4 flex flex-col gap-2">
                                    <span className="text-slate-500 text-[10px] font-bold tracking-widest uppercase">Conversão Média</span>
                                    <span className="text-2xl text-purple-400 font-black">
                                        {(
                                            performance.reduce((acc, row) => acc + (row.conversionRate || 0), 0) /
                                            (performance.length || 1) * 100
                                        ).toFixed(2)}%
                                    </span>
                                </div>
                            </div>
                            
                            <h3 className="text-white text-sm font-bold mb-4 flex items-center gap-2">
                                <TrendingUp className="w-4 h-4 text-orange-500" />
                                DIVISÃO POR ANUNCIANTE
                            </h3>

                            <div className="overflow-x-auto rounded border border-slate-800">
                                <table className="w-full text-xs font-mono border-collapse bg-slate-900/50">
                                    <thead>
                                        <tr className="border-b-2 border-slate-800 bg-slate-900">
                                            {['ANUNCIANTE', 'CLIQUES', 'TRANSAÇÕES', 'COMISSÃO', 'EPC', 'CONV %'].map(h => (
                                                <th key={h} className="py-3 px-4 text-left text-slate-500 uppercase tracking-widest text-[10px]">{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {performance.sort((a,b) => (b.commissions || 0) - (a.commissions || 0)).map((row, i) => (
                                            <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800 transition-colors">
                                                <td className="py-3 px-4 text-white font-bold">{row.advertiserName || `#${row.advertiserId}`}</td>
                                                <td className="py-3 px-4 text-slate-300">{(row.clicks ?? 0).toLocaleString('pt-BR')}</td>
                                                <td className="py-3 px-4 text-slate-300">{(row.transactions ?? 0).toLocaleString('pt-BR')}</td>
                                                <td className="py-3 px-4 text-green-400 font-bold">
                                                    R$ {(row.commissions ?? 0).toFixed(2).replace('.', ',')}
                                                </td>
                                                <td className="py-3 px-4 text-slate-400">{(row.epc ?? 0).toFixed(4)}</td>
                                                <td className="py-3 px-4 text-orange-400">
                                                    {((row.conversionRate ?? 0) * 100).toFixed(2)}%
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    )}

                    {!loading && performance.length === 0 && !error && (
                        <div className="text-center py-12 text-slate-600 bg-slate-900 border border-slate-800 rounded">
                            <BarChart2 className="w-12 h-12 mx-auto mb-3 opacity-30 text-orange-500" />
                            <p className="text-sm font-bold text-slate-400">Sem dados de performance no período.</p>
                            <p className="text-xs mt-2">Suas métricas aparecerão aqui automaticamente após a primeira venda registrada na Awin.</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default AwinProducts;
