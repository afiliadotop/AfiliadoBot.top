import React, { useState } from 'react';
import { AwinOffer } from '../../services/awin.service';
import { Tag, Copy, ExternalLink, Clock, Percent, ShoppingBag, Send } from 'lucide-react';

interface AwinOfferCardProps {
    offer: AwinOffer;
}

export const AwinOfferCard: React.FC<AwinOfferCardProps> = ({ offer }) => {
    const [copied, setCopied] = useState(false);

    const handleCopyCode = () => {
        if (offer.code) {
            navigator.clipboard.writeText(offer.code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2500);
        }
    };

    const formatExpiry = (date?: string) => {
        if (!date) return null;
        return new Date(date).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
        });
    };

    const typeLabel: Record<string, string> = {
        voucher: '🎟️ CUPOM',
        deal: '🔥 DEAL',
        product: '📦 PRODUTO',
    };

    const typeBg: Record<string, string> = {
        voucher: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
        deal: 'bg-red-500/10 border-red-500/30 text-red-400',
        product: 'bg-sky-500/10 border-sky-500/30 text-sky-400',
    };

    const advertiserName = offer.advertiser?.name || `Anunciante #${offer.advertiser?.id || offer.advertiser_id}`;
    const typeKey = offer.type || offer.promotion_type || 'deal';
    const trackingLink = offer.urlTracking || offer.tracking_link || offer.url || offer.deeplink;
    const isExpired = offer.endDate || offer.expires_at ? new Date(offer.endDate || offer.expires_at) < new Date() : false;

    const [isPublishing, setIsPublishing] = useState(false);

    const handleSendToTelegram = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        
        setIsPublishing(true);
        try {
            // Build the payload expected by your server
            const payload = {
                title: offer.title,
                description: offer.description,
                affiliate_link: trackingLink,
                short_link: trackingLink, // You can let the backend shorten if it wants
                category: "awin",
                original_price: null,
                discount_price: null,
                coupon_code: offer.code,
                coupon_expiry: offer.endDate || offer.expires_at,
                store: advertiserName,
                is_active: true
            };

            const token = localStorage.getItem('afiliadobot_token');
            const res = await fetch(`http://localhost:8000/api/telegram/post-offer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token && { 'Authorization': `Bearer ${token}` })
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                throw new Error('Falha ao disparar');
            }
            alert('Oferta disparada com sucesso no grupo Telegram!');
        } catch (err) {
            alert('Erro ao enviar oferta para o Telegram.');
            console.error(err);
        } finally {
            setIsPublishing(false);
        }
    };

    return (
        <div className={`bg-slate-950 border-2 rounded-sm flex flex-col gap-3 p-4 transition-all group ${
            isExpired ? 'border-slate-800 opacity-50' : 'border-slate-700 hover:border-orange-500'
        }`}>
            {/* Header */}
            <div className="flex items-start justify-between gap-2">
                <span className={`text-[10px] font-black tracking-widest uppercase border px-2 py-0.5 rounded-sm ${
                    typeBg[typeKey] || typeBg.deal
                }`}>
                    {typeLabel[typeKey] || '🏷️ OFERTA'}
                </span>
                {isExpired && (
                    <span className="text-[10px] font-mono text-slate-600 uppercase">EXPIRADO</span>
                )}
            </div>

            {/* Advertiser */}
            <div className="flex items-center gap-1.5">
                <ShoppingBag className="w-3.5 h-3.5 text-orange-500 flex-shrink-0" />
                <span className="text-xs font-mono text-orange-400 uppercase tracking-wider truncate" title={advertiserName}>
                    {advertiserName}
                </span>
            </div>

            {/* Title */}
            <h3 className="text-sm font-bold text-white leading-snug line-clamp-2">
                {offer.title}
            </h3>

            {/* Description */}
            {offer.description && (
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {offer.description}
                </p>
            )}

            {/* Promo Code Info */}
            {offer.code && (
                <button
                    onClick={handleCopyCode}
                    className={`flex items-center justify-between gap-2 border rounded-sm px-3 py-2 transition-all font-mono text-sm font-bold w-full mt-auto ${
                        copied
                            ? 'bg-green-500/20 border-green-500 text-green-400'
                            : 'bg-slate-900 border-slate-700 text-yellow-400 hover:border-yellow-500'
                    }`}
                >
                    <div className="flex items-center gap-2">
                        <Tag className="w-4 h-4" />
                        <span className="tracking-widest">{offer.code}</span>
                    </div>
                    <Copy className="w-3.5 h-3.5 opacity-70" />
                    {copied && <span className="text-[10px] text-green-400 ml-1">✓ COPIADO</span>}
                </button>
            )}

            {/* Expiry */}
            {(offer.endDate || offer.expires_at) && (
                <div className="flex items-center gap-1.5 text-slate-500 mt-2">
                    <Clock className="w-3 h-3" />
                    <span className="text-[10px] font-mono">
                        {isExpired ? 'EXPIROU em ' : 'Válido até '}
                        {formatExpiry(offer.endDate || offer.expires_at)}
                    </span>
                </div>
            )}

            {/* CTA Buttons */}
            <div className="flex gap-2 mt-auto pt-2 border-t border-slate-800">
                {trackingLink && (
                    <a
                        href={trackingLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-white font-black text-[10px] tracking-widest uppercase px-2 py-2.5 rounded-sm transition-colors border border-slate-700"
                    >
                        <ExternalLink className="w-3.5 h-3.5" />
                        PÁGINA
                    </a>
                )}
                
                <button
                    onClick={handleSendToTelegram}
                    disabled={isPublishing}
                    className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white font-black text-[10px] tracking-widest uppercase px-2 py-2.5 rounded-sm transition-colors border border-blue-700"
                >
                    <Send className={`w-3 h-3 ${isPublishing ? 'animate-bounce' : ''}`} />
                    TELEGRAM
                </button>
            </div>
        </div>
    );
};
