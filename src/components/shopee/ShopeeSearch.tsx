import React, { useState } from 'react';
import { Search, X } from 'lucide-react';

interface ShopeeSearchProps {
    onSearch: (keyword: string) => void;
    placeholder?: string;
    initialValue?: string;
}

export const ShopeeSearch: React.FC<ShopeeSearchProps> = ({
    onSearch,
    placeholder = "Buscar produtos na Shopee...",
    initialValue = ""
}) => {
    const [keyword, setKeyword] = useState(initialValue);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (keyword.trim()) {
            onSearch(keyword.trim());
        }
    };

    const handleClear = () => {
        setKeyword("");
        onSearch("");
    };

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
            <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-slate-400" />
                </div>

                <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder={placeholder}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 pl-12 pr-12 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                />

                {keyword && (
                    <button
                        type="button"
                        onClick={handleClear}
                        className="absolute inset-y-0 right-12 flex items-center pr-2 text-slate-400 hover:text-slate-300"
                    >
                        <X className="h-5 w-5" />
                    </button>
                )}

                <button
                    type="submit"
                    disabled={!keyword.trim()}
                    className="absolute inset-y-0 right-0 flex items-center bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed text-white font-semibold px-6 rounded-r-xl transition-all"
                >
                    Buscar
                </button>
            </div>

            {/* Quick Suggestions */}
            <div className="mt-3 flex flex-wrap gap-2">
                <span className="text-xs text-slate-500">Sugestões:</span>
                {['fone bluetooth', 'capa iphone', 'carregador', 'mouse gamer'].map((suggestion) => (
                    <button
                        key={suggestion}
                        type="button"
                        onClick={() => {
                            setKeyword(suggestion);
                            onSearch(suggestion);
                        }}
                        className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded-full transition-colors"
                    >
                        {suggestion}
                    </button>
                ))}
            </div>
        </form>
    );
};
