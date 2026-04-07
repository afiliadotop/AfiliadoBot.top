import React from 'react';
import { ShoppingBag, Flame, MapPin, Tag } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface BaseDeal {
    id: number | string;
    name: string;
    current_price: number;
    original_price: number;
    discount_percentage: number;
    image_url: string;
    affiliate_link: string;
    store: string;
    sales_count?: number;
}

interface DealCardHorizontalProps {
    deal: BaseDeal;
    className?: string;
    onClick?: (deal: BaseDeal) => void;
}

export const DealCardHorizontal: React.FC<DealCardHorizontalProps> = ({ deal, className, onClick }) => {
    // Definimos cores brutas que fujam de gradientes amigáveis
    const isAmazon = deal.store?.toLowerCase() === 'amazon';
    const storeColor = isAmazon ? 'text-cyan-400' : 'text-orange-500';
    const storeBorder = isAmazon ? 'border-cyan-500/30' : 'border-orange-500/30';
    const storeHover = isAmazon ? 'group-hover:border-cyan-400/80' : 'group-hover:border-orange-500/80';
    const bgBadge = isAmazon ? 'bg-cyan-950/40 text-cyan-400' : 'bg-orange-950/40 text-orange-400';

    const handleClick = () => {
        if (onClick) onClick(deal);
        else window.open(deal.affiliate_link, '_blank');
    };

    return (
        <div 
            onClick={handleClick}
            className={cn(
                "group flex flex-col sm:flex-row w-full bg-[#020617] cursor-pointer", // background slate-950 puro
                "border-y border-x sm:border-x-0 sm:border-y border-slate-800 transition-all duration-300",
                "hover:bg-[#0f172a] hover:z-10 relative overflow-hidden",
                "sm:rounded-none rounded-sm", // Brutalista: 0 bordas no desktop (lista corrida)
                storeHover,
                className
            )}
        >
            {/* Elemento Gota (Micro-interação de Borda) */}
            <div className={`absolute top-0 left-0 w-1 h-full opacity-0 group-hover:opacity-100 transition-opacity ${isAmazon ? 'bg-cyan-400' : 'bg-orange-500'}`} />

            {/* Imagem do Produto (Ocupa a faixa inteira verticalmente em telas grandes) */}
            <div className="relative w-full sm:w-48 h-48 sm:h-auto shrink-0 bg-slate-900 overflow-hidden flex items-center justify-center p-4">
                <img 
                    src={deal.image_url} 
                    alt={deal.name} 
                    className="w-full h-full object-contain mix-blend-lighten group-hover:scale-105 transition-transform duration-500 ease-out"
                    loading="lazy"
                />
                {deal.discount_percentage > 0 && (
                    <div className="absolute top-0 left-0 bg-red-600 text-white font-black text-sm px-2 py-1 tracking-tighter">
                        -{deal.discount_percentage}%
                    </div>
                )}
            </div>

            {/* Corpo de Conteúdo */}
            <div className="flex flex-col flex-1 p-4 sm:p-6 justify-between gap-4">
                <div className="space-y-2">
                    {/* Badge da Loja Brutalista */}
                    <div className="flex items-center gap-2">
                        <span className={cn("text-[10px] font-mono tracking-widest uppercase border px-1.5 py-0.5", storeBorder, storeColor)}>
                            {deal.store || 'SHOP'}
                        </span>
                        {(deal.sales_count ?? 0) > 0 && (
                            <span className="flex items-center gap-1 text-[10px] uppercase font-mono text-slate-500">
                                <Flame className="w-3 h-3 text-red-500" />
                                {deal.sales_count?.toLocaleString()} sold
                            </span>
                        )}
                    </div>
                    
                    {/* Título - Menos arredondamentos, tipografia reta */}
                    <h3 className="text-sm sm:text-base font-medium text-slate-200 line-clamp-2 leading-snug group-hover:text-white transition-colors">
                        {deal.name}
                    </h3>
                </div>

                {/* Bloco de Preço & CTA (Empurrado para a direita em Desktops ou Base no Mobile) */}
                <div className="flex flex-row items-end justify-between sm:justify-end gap-6 mt-auto">
                    <div className="flex flex-col">
                        {deal.original_price > deal.current_price && (
                            <span className="text-xs text-slate-500 line-through font-mono">
                                R$ {deal.original_price.toFixed(2)}
                            </span>
                        )}
                        <span className="text-2xl sm:text-3xl font-black text-white tracking-tighter">
                            <span className="text-sm text-slate-400 font-normal mr-1 tracking-normal">R$</span>
                            {deal.current_price.toFixed(2)}
                        </span>
                    </div>

                    <button className={cn(
                        "hidden sm:flex items-center justify-center gap-2 px-6 py-3 font-bold text-sm uppercase tracking-wider transition-all",
                        "border border-transparent",
                        isAmazon 
                            ? "bg-slate-800 text-cyan-400 hover:bg-cyan-400 hover:text-slate-900" 
                            : "bg-slate-800 text-orange-500 hover:bg-orange-500 hover:text-slate-900"
                    )}>
                        Pegar Oferta
                    </button>
                    
                    {/* CTA Mobile Reduzido */}
                    <button className={cn(
                        "flex sm:hidden items-center justify-center p-3 rounded-sm transition-all",
                        isAmazon ? "bg-cyan-950 text-cyan-400" : "bg-orange-950 text-orange-500"
                    )}>
                        <ShoppingBag className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
};
