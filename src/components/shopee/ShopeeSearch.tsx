import React, { useState } from 'react';
import { Search, X, Zap } from 'lucide-react';

interface ShopeeSearchProps {
    onSearch: (keyword: string) => void;
    placeholder?: string;
    initialValue?: string;
}

export const ShopeeSearch: React.FC<ShopeeSearchProps> = ({
    onSearch,
    placeholder = "BUSCAR PRODUTO OU PALAVRA-CHAVE",
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
        <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto flex flex-col items-center">
            <div className="relative w-full flex">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-orange-500" />
                </div>

                <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder={placeholder}
                    className="w-full bg-slate-950 border-2 border-slate-800 rounded-sm py-4 pl-12 pr-12 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-orange-500 transition-colors uppercase font-mono tracking-wider text-sm shadow-inner"
                />

                {keyword && (
                    <button
                        type="button"
                        onClick={handleClear}
                        className="absolute inset-y-0 right-[120px] flex items-center pr-2 text-slate-500 hover:text-red-500 transition-colors"
                        aria-label="Limpar busca"
                    >
                        <X className="h-5 w-5" />
                    </button>
                )}

                <button
                    type="submit"
                    disabled={!keyword.trim()}
                    className="absolute inset-y-0 right-0 flex items-center bg-orange-500 hover:bg-orange-400 disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed text-slate-950 font-black px-8 rounded-r-sm transition-all border-l-2 border-slate-800 uppercase tracking-widest text-sm"
                >
                    BUSCAR
                </button>
            </div>

            {/* Quick Suggestions Brutalistas */}
            <div className="mt-4 flex flex-wrap gap-2 justify-center items-center">
                <span className="text-xs text-orange-500/80 font-mono font-bold flex items-center gap-1 uppercase tracking-widest">
                    <Zap className="w-3 h-3" /> Tendências:
                </span>
                {['creatina', 'fone bluetooth', 'airfryer', 'iphone'].map((suggestion) => (
                    <button
                        key={suggestion}
                        type="button"
                        onClick={() => {
                            setKeyword(suggestion);
                            onSearch(suggestion);
                        }}
                        className="text-xs bg-slate-900 border border-slate-700 hover:border-orange-500 text-slate-400 hover:text-orange-400 px-3 py-1 rounded-sm transition-all uppercase tracking-widest font-mono select-none"
                    >
                        {suggestion}
                    </button>
                ))}
            </div>
        </form>
    );
};
