import React, { useEffect, useState } from 'react';
import { DealCardHorizontal, BaseDeal } from './DealCardHorizontal';
import { Loader2, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const LiveBotFeed = () => {
    const [deals, setDeals] = useState<BaseDeal[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        // Simulando delay de raspagem em milisegundos para o usuário ver o Spinner e pensar 'está puxando agora'
        const timer = setTimeout(() => {
            setDeals([
                {
                    id: 'mock-1',
                    name: 'Fritadeira Air Fryer Mondial 4L Family - Painel Inox AF-14',
                    current_price: 269.90,
                    original_price: 549.90,
                    discount_percentage: 51,
                    image_url: 'https://m.media-amazon.com/images/I/71u9D99JsyL._AC_SX679_.jpg',
                    affiliate_link: '#',
                    store: 'amazon',
                    sales_count: 8520
                },
                {
                    id: 'mock-2',
                    name: 'Smartphone Samsung Galaxy S23 Ultra 5G 256GB Tela 6.8"',
                    current_price: 4999.00,
                    original_price: 9499.00,
                    discount_percentage: 47,
                    image_url: 'https://m.media-amazon.com/images/I/71w1jY8tVKL._AC_SX679_.jpg',
                    affiliate_link: '#',
                    store: 'shopee',
                    sales_count: 145
                },
                {
                    id: 'mock-3',
                    name: 'Smart TV 55" UHD 4K Samsung 55CU7700, Processador Crystal 4K',
                    current_price: 2199.00,
                    original_price: 3599.00,
                    discount_percentage: 39,
                    image_url: 'https://m.media-amazon.com/images/I/71Zp+i6E2IL._AC_SX679_.jpg',
                    affiliate_link: '#',
                    store: 'amazon',
                    sales_count: 532
                }
            ]);
            setLoading(false);
        }, 1200);

        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-center my-20 px-4">
            {/* Cabecalho da Vitrine */}
            <div className="flex flex-col items-center mb-10 text-center">
                <div className="flex items-center gap-2 px-3 py-1 bg-green-950/30 border border-green-500/20 text-green-400 text-xs font-mono uppercase tracking-widest mb-4">
                    <Zap className="w-3 h-3 animate-pulse text-green-500" />
                    <span>Live Bot Feed</span>
                </div>
                <h2 className="text-3xl md:text-5xl font-black text-white tracking-tighter uppercase leading-none">
                    Interceptações Recentes
                </h2>
                <p className="text-slate-400 mt-4 max-w-xl text-sm md:text-base font-medium">
                    Veja em tempo real o que nossos sub-bots rasparam das entranhas das lojas nos últimos 60 minutos.
                </p>
            </div>

            {/* A Cortina (Fading) - Container das Listas */}
            <div className="relative w-full flex flex-col bg-[#0f172a] border border-slate-800 rounded-sm">
                
                {loading ? (
                    <div className="flex flex-col items-center justify-center py-32 space-y-4">
                        <Loader2 className="w-8 h-8 animate-spin text-green-500" />
                        <span className="text-green-500 font-mono text-sm tracking-widest uppercase">Raspando a Superfície...</span>
                    </div>
                ) : (
                    <div className="flex flex-col">
                        {deals.map((deal, idx) => (
                            <DealCardHorizontal 
                                key={deal.id} 
                                deal={deal} 
                            />
                        ))}
                    </div>
                )}

                {/* Fade Cortina - Induz o Registro */}
                {!loading && (
                    <div className="absolute bottom-0 left-0 w-full h-48 bg-gradient-to-t from-[#020617] via-[#020617]/80 to-transparent flex flex-col items-center justify-end pb-8 pointer-events-none">
                        <div className="pointer-events-auto flex flex-col items-center gap-4 translate-y-4 hover:-translate-y-1 transition-transform">
                            <span className="text-slate-400 font-mono text-[10px] uppercase tracking-widest">
                                +3.421 outras ofertas ocultas
                            </span>
                            <button 
                                onClick={() => navigate('/register')}
                                className="bg-green-500 text-[#020617] font-black uppercase tracking-widest text-sm px-8 py-4 sm:rounded-none rounded-sm hover:bg-green-400 transition-colors shadow-[0_0_30px_-5px_rgba(34,197,94,0.4)]"
                            >
                                Desbloquear Radar Completo
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
