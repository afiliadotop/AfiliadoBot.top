import { Bot, ArrowRight, Link as LinkIcon, TrendingUp, Sparkles, Menu, X, Zap } from "lucide-react";
import React, { useState } from "react";
import { LiveBotFeed } from "../components/ui/LiveBotFeed";
import { useNavigate } from "react-router-dom";

export const LandingPage = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const navigate = useNavigate();

    const handleLogin = () => navigate('/dashboard/overview');

    return (
        <div className="min-h-screen bg-[#020617] text-slate-50 font-sans selection:bg-orange-500 selection:text-white">
            {/* Navigation Base Brutalista */}
            <nav className="border-b border-slate-800 bg-[#020617]/90 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 border-2 border-green-500 rounded-sm flex items-center justify-center bg-green-500/10 shadow-[0_0_10px_-2px_rgba(34,197,94,0.3)]">
                                <Bot className="w-5 h-5 text-green-500" />
                            </div>
                            <span className="text-xl font-black text-white tracking-widest uppercase">
                                Afiliado<span className="text-green-500">Bot</span>
                            </span>
                        </div>

                        <div className="hidden md:flex items-center gap-8">
                            <a href="#features" className="text-sm font-bold tracking-widest uppercase text-slate-400 hover:text-white transition-colors">Funcionalidades</a>
                            <a href="#pricing" className="text-sm font-bold tracking-widest uppercase text-slate-400 hover:text-white transition-colors">Planos</a>
                            <button
                                onClick={handleLogin}
                                className="bg-orange-500 hover:bg-orange-400 text-[#020617] px-6 py-2 rounded-sm text-sm font-black uppercase tracking-widest transition-all shadow-[0_0_20px_-5px_rgba(249,115,22,0.6)]"
                            >
                                Acessar Bot
                            </button>
                        </div>

                        <button
                            className="md:hidden text-slate-300"
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                        >
                            {isMenuOpen ? <X /> : <Menu />}
                        </button>
                    </div>
                </div>

                {/* Mobile Menu */}
                {isMenuOpen && (
                    <div className="md:hidden bg-[#020617] border-b border-slate-800 p-4 space-y-4">
                        <a href="#features" className="block text-slate-300 font-bold uppercase tracking-widest hover:text-white">Funcionalidades</a>
                        <button
                            onClick={handleLogin}
                            className="w-full bg-orange-500 text-[#020617] px-4 py-3 rounded-sm font-black uppercase tracking-widest"
                        >
                            Acessar Bot
                        </button>
                    </div>
                )}
            </nav>

            {/* Hero Section Brutalista */}
            <header className="relative pt-24 pb-20 overflow-hidden">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-green-500/10 rounded-full blur-[100px] -z-10" />
                <div className="absolute top-1/3 right-1/4 w-[400px] h-[200px] bg-orange-500/10 rounded-full blur-[100px] -z-10" />
                
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center flex flex-col items-center">
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#0f172a] border border-orange-500/30 text-orange-400 text-xs font-mono uppercase tracking-widest mb-8">
                        <span className="w-2 h-2 bg-orange-500 animate-pulse" />
                        Nova Engine de Amazon Scraper Ativa
                    </div>
                    
                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-6 uppercase leading-[0.9]">
                        A Máquina de <br />
                        <span className="text-green-500">Lucro Automático</span>
                    </h1>
                    
                    <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed font-medium">
                        Conecte seu Telegram e deixe a inteligência artificial varrer milhares de ofertas, encurtar links e postar automaticamente.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row gap-6 justify-center items-center w-full">
                        <button
                            onClick={handleLogin}
                            className="group bg-orange-500 text-[#020617] px-10 py-4 rounded-sm font-black uppercase tracking-widest hover:bg-orange-400 transition-all shadow-[0_0_30px_-5px_rgba(249,115,22,0.4)] flex items-center justify-center gap-3 w-full sm:w-auto"
                        >
                            <Zap className="w-5 h-5" />
                            Iniciar Bot Agora
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </button>
                    </div>
                </div>
            </header>

            {/* Injeção da Vixtrine "Amostra Grátis" */}
            <LiveBotFeed />

            {/* Features Grid Brutalista */}
            <section id="features" className="py-24 bg-[#020617] border-t border-slate-900">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-3 gap-6">
                        <FeatureCard
                            icon={<LinkIcon className="w-6 h-6 text-green-400" />}
                            title="Conversor em Massa"
                            description="Jogue links da Shopee ou Amazon, o sistema cospe links com seu afiliado pronto para venda."
                        />
                        <FeatureCard
                            icon={<TrendingUp className="w-6 h-6 text-orange-400" />}
                            title="Monitor Atirador"
                            description="Nossos robôs varrem a madrugada atrás de quedas bruscas de preço para te notificar."
                        />
                        <FeatureCard
                            icon={<Sparkles className="w-6 h-6 text-cyan-400" />}
                            title="Copy de IA"
                            description="Geração instantânea de legenda persuasiva com gatilhos mentais para Telegram/Insta."
                        />
                    </div>
                </div>
            </section>
        </div>
    );
};

const FeatureCard = ({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) => (
    <div className="p-8 rounded-2xl bg-slate-950 border border-slate-800 hover:border-indigo-500/50 transition-colors group">
        <div className="w-12 h-12 bg-slate-900 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            {icon}
        </div>
        <h3 className="text-xl font-bold mb-3 text-slate-100">{title}</h3>
        <p className="text-slate-400 leading-relaxed">{description}</p>
    </div>
);
