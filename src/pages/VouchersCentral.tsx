import React, { useEffect, useState } from 'react';
import { awinService, AwinOffer } from '../services/awin.service';
import { Tag, Store, Search, Scissors, Loader2, Sparkles } from 'lucide-react';

export const VouchersCentral: React.FC = () => {
    const [vouchers, setVouchers] = useState<AwinOffer[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [copiedId, setCopiedId] = useState<number | null>(null);

    useEffect(() => {
        const fetchVouchers = async () => {
            try {
                const res = await awinService.getPublicVouchers();
                if (res && res.data) {
                    setVouchers(res.data);
                }
            } catch (err) {
                console.error("Failed to load public vouchers", err);
            } finally {
                setLoading(false);
            }
        };
        fetchVouchers();
    }, []);

    const copyCode = (id: number, code: string) => {
        navigator.clipboard.writeText(code);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 3000);
    };

    const filtered = vouchers.filter(v => {
        if (!search) return true;
        const term = search.toLowerCase();
        return (
            (v.title || '').toLowerCase().includes(term) ||
            (v.advertiser?.name || '').toLowerCase().includes(term) ||
            (v.code || '').toLowerCase().includes(term)
        );
    });

    // Helper: Gerar JSON-LD Schema
    const structuredData = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": filtered.map((v, idx) => ({
            "@type": "ListItem",
            "position": idx + 1,
            "item": {
                "@type": "SaleEvent",
                "name": v.title,
                "description": v.description,
                "startDate": v.starts_at || new Date().toISOString(),
                "endDate": v.expires_at || v.endDate,
                "url": v.tracking_link || v.urlTracking || v.deeplink,
                "eventStatus": "https://schema.org/EventScheduled",
                "organizer": {
                    "@type": "Organization",
                    "name": v.advertiser?.name || "Loja"
                }
            }
        }))
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans transition-colors">
            {/* INJECT SEO METADATA */}
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }} />

            <div className="max-w-6xl mx-auto px-4 py-12">
                <div className="text-center mb-12">
                    <div className="inline-flex items-center justify-center space-x-2 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 font-bold px-4 py-1.5 rounded-full text-xs uppercase tracking-widest mb-4">
                        <Sparkles size={14} className="animate-pulse" />
                        <span>Parcerias VIP Autenticadas</span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-black text-slate-900 dark:text-white mb-4">
                        Central de <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-rose-500">Cupons</span>
                    </h1>
                    <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
                        Acesso direto aos cupons e vouchers restritos das marcas oficiais. 
                        Copie o código antes de finalizar o carrinho.
                    </p>
                </div>

                {/* Busca */}
                <div className="relative max-w-xl mx-auto mb-12">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                    <input 
                        type="search" 
                        placeholder="Buscar por loja (ex: Kabum, Nike) ou nome..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-12 pr-4 py-4 rounded-xl bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 focus:border-orange-500 dark:focus:border-orange-500 outline-none text-slate-700 dark:text-slate-200 shadow-sm transition-all"
                    />
                </div>

                {loading ? (
                    <div className="flex flex-col items-center justify-center py-20 text-slate-500">
                        <Loader2 className="w-12 h-12 animate-spin mb-4 text-orange-500" />
                        <p className="font-mono text-sm tracking-widest uppercase">Caçando ofertas ativas...</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filtered.length > 0 ? (
                            filtered.map((v) => (
                                <div key={v.promotionId || v.awin_offer_id} className="group relative bg-white dark:bg-slate-900 rounded-2xl border-2 border-slate-100 dark:border-slate-800 hover:border-orange-500/50 dark:hover:border-orange-500/50 shadow-sm hover:shadow-xl transition-all overflow-hidden flex flex-col h-full">
                                    <div className="h-2 w-full bg-gradient-to-r from-orange-500 to-rose-500"></div>
                                    <div className="flex-1 p-6 relative">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700">
                                                <Store size={14} className="text-slate-500" />
                                                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                                                    {v.advertiser?.name || v.advertiser_name || "Loja Oficial"}
                                                </span>
                                            </div>
                                            {/* (v as any).image_url passed from our custom endpoint payload injection */}
                                            {(v as any).image_url ? (
                                                <img src={(v as any).image_url} alt={v.advertiser?.name} className="w-10 h-10 object-contain rounded bg-white shadow-sm border border-slate-100" />
                                            ) : (
                                                <Tag size={20} className="text-orange-500" />
                                            )}
                                        </div>

                                        <h3 className="text-lg font-black text-slate-900 dark:text-white leading-tight mb-3">
                                            {v.title}
                                        </h3>
                                        <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-3 mb-6">
                                            {v.description || "Oferta especial de compra."}
                                        </p>

                                        {v.code && (
                                            <div className="absolute -left-2 top-1/2 -translate-y-1/2 w-4 h-8 bg-slate-50 dark:bg-slate-950 rounded-r-full border-r border-slate-200 dark:border-slate-800"></div>
                                        )}
                                        {v.code && (
                                            <div className="absolute -right-2 top-1/2 -translate-y-1/2 w-4 h-8 bg-slate-50 dark:bg-slate-950 rounded-l-full border-l border-slate-200 dark:border-slate-800"></div>
                                        )}
                                    </div>

                                    <div className="p-6 pt-0 border-t border-dashed border-slate-200 dark:border-slate-800 mt-auto bg-slate-50/50 dark:bg-slate-900/50">
                                        {v.code ? (
                                            <div className="mt-6 flex flex-col gap-3">
                                                <span className="text-[10px] uppercase tracking-widest font-bold text-slate-400 text-center">Código do Cupom</span>
                                                <div className="flex items-center w-full bg-slate-100 dark:bg-slate-950 border-2 border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden group-hover:border-orange-500/30 transition-colors">
                                                    <div className="px-4 py-3 flex-1 font-mono text-center font-bold tracking-wider text-slate-800 dark:text-slate-200">
                                                        {v.code}
                                                    </div>
                                                    <button 
                                                        onClick={(e) => { e.preventDefault(); copyCode(v.promotionId || 0, v.code!); }}
                                                        className={`h-full px-5 flex items-center justify-center border-l-2 border-slate-200 dark:border-slate-800 transition-colors ${
                                                            copiedId === (v.promotionId || 0) 
                                                                ? 'bg-green-500 text-white border-green-500' 
                                                                : 'bg-white dark:bg-slate-800 text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-500/10'
                                                        }`}
                                                    >
                                                        {copiedId === (v.promotionId || 0) ? <span className="text-xs font-bold uppercase">Copiado!</span> : <Scissors size={18} />}
                                                    </button>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="mt-6">
                                                <span className="block text-[10px] uppercase tracking-widest font-bold text-slate-400 text-center mb-3">Ativação Mágica</span>
                                                <div className="w-full text-center py-3 rounded-xl border-2 border-dashed border-orange-200 dark:border-orange-500/20 text-orange-500 font-bold bg-orange-50 dark:bg-orange-500/5">
                                                    Ativado no Site
                                                </div>
                                            </div>
                                        )}

                                        <a 
                                            href={v.urlTracking || v.deeplink || "#"} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            className="mt-4 w-full block text-center bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-bold py-3.5 rounded-xl hover:opacity-90 transition-opacity uppercase text-xs tracking-wider"
                                        >
                                            Ir para Loja Completa
                                        </a>
                                        {v.expires_at || v.endDate ? (
                                            <p className="text-center text-[10px] text-red-500 font-medium mt-3">
                                                ⏳ Expira em: {new Date(v.expires_at || v.endDate!).toLocaleDateString('pt-BR')}
                                            </p>
                                        ) : null}
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="col-span-full text-center py-16 text-slate-500">
                                <Tag size={48} className="mx-auto mb-4 opacity-20" />
                                <p className="text-lg">Ops! Nenhum cupom bateu com sua busca.</p>
                                <button onClick={() => setSearch('')} className="mt-4 text-orange-500 font-bold hover:underline">Limpar busca</button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};
