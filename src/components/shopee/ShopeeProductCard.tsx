import React, { useState } from 'react';
import { ShopeeProduct } from '../../services/shopee.service';
import { ShoppingBag, Star, TrendingUp, Package, Send } from 'lucide-react';
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
    const commission = product.commissionRate ? parseFloat(product.commissionRate) * 100 : 0;

    const handleClick = () => {
        if (onLinkClick) {
            onLinkClick(product);
        } else {
            window.open(product.offerLink, '_blank');
        }
    };

    const handleSendToTelegram = async (e: React.MouseEvent) => {
        e.stopPropagation();
        setSending(true);

        try {
            const { shopeeService } = await import('../../services/shopee.service');
            const result = await shopeeService.sendProductToTelegram(product.itemId, product);

            if (result?.success) {
                // Success toast
                const toast = document.createElement('div');
                toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in';
                toast.textContent = `✅ ${result.message}`;
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);
            } else {
                throw new Error('Erro ao enviar');
            }
        } catch (error: any) {
            // Error toast
            const toast = document.createElement('div');
            toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in';
            toast.textContent = `❌ ${error?.response?.data?.detail || 'Erro ao enviar para Telegram'}`;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 4000);
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-slate-700 transition-all hover:shadow-lg hover:shadow-orange-500/10">
            {/* Image */}
            <div className="relative aspect-square bg-slate-800">
                {/* Favorite Button - Top Left */}
                <div className="absolute top-2 left-2 z-20">
                    <FavoriteButton itemId={product.itemId} />
                </div>

                <img
                    src={product.imageUrl}
                    alt={product.productName}
                    className="w-full h-full object-cover"
                    loading="lazy"
                />

                {/* Discount Badge - Top Right */}
                {product.discountRate > 0 && (
                    <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded-lg text-xs font-bold z-10">
                        🔥 {product.discountRate}% OFF
                    </div>
                )}

                {/* Commission Badge - Bottom Left */}
                {showCommission && commission > 0 && (
                    <div className={`absolute bottom-2 left-2 px-2 py-1 rounded-lg text-xs font-bold z-10 ${commission >= 50
                        ? 'bg-yellow-500 text-slate-900'
                        : 'bg-green-500/90 text-white'
                        }`}>
                        💰 {commission.toFixed(1)}%
                    </div>
                )}
            </div>

            {/* Content */}
            <div className="p-4 space-y-3">
                {/* Product Name */}
                <h3 className="text-sm font-medium text-slate-100 line-clamp-2 min-h-[40px]">
                    {product.productName}
                </h3>

                {/* Price */}
                <div className="flex items-baseline gap-2">
                    {priceMin === priceMax ? (
                        <span className="text-2xl font-bold text-orange-400">
                            R$ {priceMin.toFixed(2)}
                        </span>
                    ) : (
                        <>
                            <span className="text-xl font-bold text-orange-400">
                                R$ {priceMin.toFixed(2)}
                            </span>
                            <span className="text-sm text-slate-400">
                                - R$ {priceMax.toFixed(2)}
                            </span>
                        </>
                    )}
                </div>

                {/* Social Proof */}
                <div className="flex items-center gap-4 text-xs text-slate-400">
                    <div className="flex items-center gap-1">
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        <span>{product.rating || 'N/A'}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Package className="w-3 h-3" />
                        <span>{product.sales.toLocaleString()} vendidos</span>
                    </div>
                </div>

                {/* Shop Name */}
                <div className="text-xs text-slate-500 truncate">
                    🏪 {product.shopName}
                </div>

                {/* Commission Details - Admin Only */}
                {showCommission && product.commissionAmount && (
                    <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-2 space-y-1">
                        <div className="flex items-center justify-between text-xs">
                            <span className="text-green-400 font-medium">Comissão por venda:</span>
                            <span className="text-green-300 font-bold">
                                R$ {parseFloat(product.commissionAmount).toFixed(2)}
                            </span>
                        </div>
                        {product.sellerCommissionRate && (
                            <div className="text-[10px] text-green-300/60">
                                Vendedor: {(parseFloat(product.sellerCommissionRate) * 100).toFixed(1)}%
                                {product.shopeeCommissionRate && ` | Shopee: ${(parseFloat(product.shopeeCommissionRate) * 100).toFixed(1)}%`}
                            </div>
                        )}
                    </div>
                )}

                {/* Telegram Share Button */}
                <button
                    onClick={handleSendToTelegram}
                    disabled={sending}
                    className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed text-white font-semibold py-2.5 px-4 rounded-lg transition-all flex items-center justify-center gap-2 group"
                >
                    <Send className={`w-4 h-4 ${sending ? 'animate-pulse' : 'group-hover:scale-110 transition-transform'}`} />
                    {sending ? 'Enviando...' : 'Enviar ao Telegram'}
                </button>

                {/* CTA Button */}
                <button
                    onClick={handleClick}
                    className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold py-2.5 px-4 rounded-lg transition-all flex items-center justify-center gap-2 group"
                >
                    <ShoppingBag className="w-4 h-4 group-hover:scale-110 transition-transform" />
                    {showCommission ? 'Ver Produto e Ganhar' : 'Ver Oferta'}
                </button>
            </div>
        </div>
    );
};
