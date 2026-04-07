import React, { useState } from 'react';
import { ShopeeProduct } from '../../services/shopee.service';
import { ShoppingBag, Star, Package, Send, Link as LinkIcon, DollarSign, Zap, Crown, ShieldCheck } from 'lucide-react';
import { FavoriteButton } from './FavoriteButton';

interface ShopeeProductCardProps {
    product: ShopeeProduct;
    showCommission?: boolean;
    onLinkClick?: (product: ShopeeProduct) => void;
}

export const ShopeeProductCard: React.FC<ShopeeProductCardProps> = ({
    product,
    showCommission = false,
    onLinkClick
}) => {
    const [sending, setSending] = useState(false);

    const priceMin = parseFloat(product.priceMin);
    const priceMax = parseFloat(product.priceMax);
    const commissionRate = product.commissionRate ? parseFloat(product.commissionRate) : 0;
    const commissionPct = commissionRate * 100;
    const estProfitMin = priceMin * commissionRate;

    const handleClick = () => {
        if (onLinkClick) {
            onLinkClick(product);
        } else {
            window.open(product.offerLink, '_blank');
        }
    };

    const handleCopyLink = (e: React.MouseEvent) => {
        e.stopPropagation();
        navigator.clipboard.writeText(product.offerLink);
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-slate-800 border-l-4 border-orange-500 text-white px-6 py-3 rounded shadow-xl z-50 animate-slide-in font-mono text-sm';
        toast.textContent = `📋 Link copiado!`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
    };

    const handleSendToTelegram = async (e: React.MouseEvent) => {
        e.stopPropagation();
        setSending(true);

        try {
            const { shopeeService } = await import('../../services/shopee.service');
            
            // 1. Busca detalhes estendidos (Vídeo e Reviews) para Prova Social
            const extendedData = await shopeeService.getExtendedDetails(product.itemId, product.shopId);
            
            // 2. Mescla os dados
            const finalData = {
                ...product,
                videoUrl: extendedData?.videoUrl,
                reviews: extendedData?.reviews || []
            };

            // 3. Envia para o Telegram
            const result = await shopeeService.sendProductToTelegram(product.itemId, finalData);

            if (result?.success) {
                const toast = document.createElement('div');
                toast.className = 'fixed top-4 right-4 bg-slate-800 border-l-4 border-blue-500 text-white px-6 py-3 rounded shadow-xl z-50 animate-slide-in font-mono text-sm';
                toast.textContent = `✅ Vídeo e Reviews enviados com sucesso!`;
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);
            } else {
                throw new Error('Erro ao enviar');
            }
        } catch (error: any) {
            const toast = document.createElement('div');
            toast.className = 'fixed top-4 right-4 bg-slate-900 border-l-4 border-red-500 text-white px-6 py-3 rounded shadow-xl z-50 animate-slide-in font-mono text-sm';
            toast.textContent = `❌ ${error?.response?.data?.detail || 'Falha no Telegram'}`;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 4000);
        } finally {
            setSending(false);
        }
    };

    // Identificação de Autoridade da Loja
    const isMall = product.shopType === 1;
    const isStar = product.shopType === 2 || product.shopType === 4;

    return (
        <div className="bg-slate-950 border-2 border-slate-800 rounded-sm overflow-hidden hover:border-slate-500 transition-all flex flex-col group relative">
            
            {/* Indicador superior Brutalista */}
            <div className="h-1 w-full bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800 group-hover:from-orange-500 group-hover:to-orange-400 transition-colors"></div>

            {/* Imagem (Area Superior) */}
            <div className="relative aspect-square bg-white border-b-2 border-slate-800">
                <div className="absolute top-3 left-3 z-20 bg-slate-900/80 backdrop-blur rounded p-1">
                    <FavoriteButton itemId={product.itemId} />
                </div>

                <img
                    src={product.imageUrl}
                    alt={product.productName}
                    className="w-full h-full object-contain p-2"
                    loading="lazy"
                />

                {/* Etiquetas Superiores */}
                {product.discountRate >= 40 ? (
                    <div className="absolute top-0 right-0 bg-red-600 text-white px-3 py-1.5 font-mono text-[10px] font-black z-10 rounded-bl-xl shadow-lg border-b-2 border-l-2 border-red-800 flex items-center gap-1 animate-pulse">
                        <Zap className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        RELÂMPAGO {product.discountRate}% OFF
                    </div>
                ) : product.discountRate > 0 ? (
                    <div className="absolute top-0 right-0 bg-slate-900 text-white px-3 py-1 font-mono text-xs font-bold z-10 rounded-bl-sm">
                        -{product.discountRate}%
                    </div>
                ) : null}

                {/* Etiquetas Inferiores de Autoridade (MALL/INDICADA) */}
                {isMall && (
                    <div className="absolute bottom-0 left-0 w-full bg-slate-950/90 backdrop-blur-sm px-3 py-1.5 z-10 border-t border-yellow-600/30 flex items-center justify-center gap-1.5">
                        <Crown className="w-4 h-4 text-yellow-500" />
                        <span className="text-yellow-500 text-[10px] font-black tracking-widest uppercase">
                            Shopee Mall
                        </span>
                    </div>
                )}
                
                {isStar && !isMall && (
                    <div className="absolute bottom-0 left-0 w-full bg-orange-600/90 backdrop-blur-sm px-3 py-1.5 z-10 flex items-center justify-center gap-1.5">
                        <ShieldCheck className="w-4 h-4 text-white" />
                        <span className="text-white text-[10px] font-black tracking-widest uppercase">
                            Loja Indicada
                        </span>
                    </div>
                )}
            </div>

            {/* Conteúdo Inferior Sombrio */}
            <div className="p-4 space-y-4 flex flex-col flex-grow">
                {/* Título */}
                <h3 className="text-sm font-semibold text-slate-200 line-clamp-2 leading-tight min-h-[40px]">
                    {product.productName}
                </h3>

                {/* Preços e Lucro */}
                <div className="space-y-1 bg-slate-900 p-3 border border-slate-800 rounded-sm">
                    <div className="flex items-baseline gap-2">
                        <span className="text-2xl font-black text-slate-100 font-mono tracking-tighter">
                            R$ {priceMin.toFixed(2)}
                        </span>
                        {priceMin !== priceMax && (
                            <span className="text-xs text-slate-500 font-mono line-through">
                                R$ {priceMax.toFixed(2)}
                            </span>
                        )}
                    </div>
                    
                    {/* Destaque Financeiro - Lucro em Reais */}
                    {showCommission && commissionRate > 0 && (
                        <div className="flex items-center gap-1.5 text-green-400 mt-1">
                            <DollarSign className="w-4 h-4" />
                            <span className="text-sm font-bold uppercase tracking-wider">
                                Lucro ~ R$ {estProfitMin.toFixed(2)}
                            </span>
                            <span className="text-[10px] ml-auto text-green-500/50 bg-green-500/10 px-1.5 rounded">
                                {commissionPct.toFixed(1)}%
                            </span>
                        </div>
                    )}
                </div>

                {/* Stats */}
                <div className="flex items-center justify-between text-xs text-slate-400 font-mono uppercase tracking-widest pt-2">
                    <div className="flex items-center gap-1">
                        <Star className="w-3.5 h-3.5 fill-slate-500 text-slate-500" />
                        <span>{product.rating || 'S/N'}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Package className="w-3.5 h-3.5" />
                        <span>{product.sales >= 1000 ? `${(product.sales / 1000).toFixed(1)}k` : product.sales} Vendas</span>
                    </div>
                </div>

                <div className="flex-grow"></div>

                {/* Ações Brutalistas */}
                <div className="grid grid-cols-5 gap-2 pt-2">
                    {/* Botão de Cópia (Menor) */}
                    <button
                        onClick={handleCopyLink}
                        className="col-span-1 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center justify-center rounded-sm transition-colors"
                        title="Copiar Link"
                    >
                        <LinkIcon className="w-4 h-4" />
                    </button>

                    {/* Botão Principal Ver Oferta (Para Cliente) ou Ir pra página */}
                    <button
                        onClick={handleClick}
                        className="col-span-4 bg-slate-100 hover:bg-white text-slate-900 border-2 border-slate-100 font-bold py-2 px-3 rounded-sm transition-all flex items-center justify-center gap-2 text-sm uppercase tracking-wider"
                    >
                        <ShoppingBag className="w-4 h-4" />
                        Acessar
                    </button>
                </div>
                
                {/* Botão VIP (Apenas Admin) */}
                <button
                    onClick={handleSendToTelegram}
                    disabled={sending}
                    className="w-full bg-[#0088cc]/10 hover:bg-[#0088cc]/20 border border-[#0088cc]/50 text-[#00aaff] hover:text-white disabled:opacity-50 font-bold py-2.5 px-4 rounded-sm transition-all flex items-center justify-center gap-2 uppercase tracking-widest text-xs mt-1"
                >
                    <Send className={`w-4 h-4 ${sending ? 'animate-pulse' : ''}`} />
                    {sending ? 'Disparando...' : 'Bot Telegram VIP'}
                </button>
            </div>
        </div>
    );
};
