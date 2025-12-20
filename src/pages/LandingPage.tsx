import { Bot, ArrowRight, Link as LinkIcon, TrendingUp, Sparkles, Menu, X } from "lucide-react";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export const LandingPage = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const navigate = useNavigate();

    const handleLogin = () => navigate('/dashboard/overview');

    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-indigo-500 selection:text-white">
            {/* Navigation */}
            <nav className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
                                AfiliadoBot
                            </span>
                        </div>

                        <div className="hidden md:flex items-center gap-8">
                            <a href="#features" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Funcionalidades</a>
                            <a href="#pricing" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Planos</a>
                            <button
                                onClick={handleLogin}
                                className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2 rounded-full text-sm font-semibold transition-all shadow-[0_0_20px_-5px_rgba(99,102,241,0.5)]"
                            >
                                Acessar Dashboard
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
                    <div className="md:hidden bg-slate-900 border-b border-slate-800 p-4 space-y-4">
                        <a href="#features" className="block text-slate-300 hover:text-white">Funcionalidades</a>
                        <button
                            onClick={handleLogin}
                            className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium"
                        >
                            Acessar Dashboard
                        </button>
                    </div>
                )}
            </nav>

            {/* Hero Section */}
            <header className="relative pt-20 pb-32 overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] -z-10" />
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/50 border border-indigo-500/30 text-indigo-300 text-xs font-medium mb-6 animate-fade-in-up">
                        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                        Novo: Análise de Concorrência & Importação CSV
                    </div>
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
                        Maximize seus ganhos com <br />
                        <span className="text-indigo-400">Telegram & IA</span>
                    </h1>
                    <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
                        A plataforma completa para gerenciar links de afiliados, rastrear conversões e criar copys de vendas automáticas usando inteligência artificial.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                        <button
                            onClick={handleLogin}
                            className="group bg-white text-slate-950 px-8 py-3.5 rounded-full font-bold text-lg hover:bg-slate-200 transition-all flex items-center gap-2"
                        >
                            Começar Agora
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button className="px-8 py-3.5 rounded-full font-semibold text-slate-300 border border-slate-700 hover:bg-slate-800 transition-all">
                            Ver Demo do Bot
                        </button>
                    </div>
                </div>
            </header>

            {/* Features Grid */}
            <section id="features" className="py-24 bg-slate-900/50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={<LinkIcon className="w-6 h-6 text-indigo-400" />}
                            title="Gerenciador de Links"
                            description="Importe CSVs da Shopee/AliExpress e organize seus links automaticamente."
                        />
                        <FeatureCard
                            icon={<TrendingUp className="w-6 h-6 text-purple-400" />}
                            title="Análise de Concorrência"
                            description="Monitore preços e receba alertas quando seus concorrentes baixarem os preços."
                        />
                        <FeatureCard
                            icon={<Sparkles className="w-6 h-6 text-pink-400" />}
                            title="IA Generativa"
                            description="Crie legendas persuasivas para seus posts com nossa integração Google Gemini."
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
