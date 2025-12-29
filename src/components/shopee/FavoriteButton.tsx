import React, { useState } from 'react';
import { Heart, Loader2 } from 'lucide-react';
import { shopeeService } from '../../services/shopee.service';
import { toast } from 'sonner';

interface FavoriteButtonProps {
    itemId: number;
    initialFavorited?: boolean;
    onToggle?: (isFavorite: boolean) => void;
    className?: string;
}

export const FavoriteButton: React.FC<FavoriteButtonProps> = ({
    itemId,
    initialFavorited = false,
    onToggle,
    className = ''
}) => {
    const [isFavorite, setIsFavorite] = useState(initialFavorited);
    const [loading, setLoading] = useState(false);

    const handleToggle = async (e: React.MouseEvent) => {
        e.stopPropagation();
        e.preventDefault();

        setLoading(true);
        try {
            if (isFavorite) {
                await shopeeService.removeFavorite(itemId);
                toast.success('Removido dos favoritos');
            } else {
                await shopeeService.addFavorite(itemId);
                toast.success('❤️ Adicionado aos favoritos!');
            }

            const newState = !isFavorite;
            setIsFavorite(newState);
            onToggle?.(newState);
        } catch (error: any) {
            if (error?.status === 409) {
                toast.info('Produto já está nos favoritos');
                setIsFavorite(true);
            } else {
                toast.error('Erro ao atualizar favoritos');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <button
            onClick={handleToggle}
            disabled={loading}
            className={`p-2 rounded-full hover:bg-white/10 dark:hover:bg-gray-700 
        transition-all backdrop-blur-sm bg-black/20 disabled:opacity-50 
        disabled:cursor-not-allowed ${className}`}
            title={isFavorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
        >
            {loading ? (
                <Loader2 className="w-5 h-5 animate-spin text-red-500" />
            ) : (
                <Heart
                    className={`w-5 h-5 transition-all ${isFavorite
                            ? 'fill-red-500 text-red-500 scale-110'
                            : 'text-gray-400 hover:text-red-400'
                        }`}
                />
            )}
        </button>
    );
};
