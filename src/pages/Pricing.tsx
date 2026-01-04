import React from "react";
import { useNavigate } from "react-router-dom";
import { Check, Zap, Shield, TrendingUp, Bot } from "lucide-react";
import { PageTransition } from "../components/layout/PageTransition";
import { toast } from "sonner";

export const Pricing = () => {
    const navigate = useNavigate();

    const handleSubscribe = () => {
        toast.info("Redirecionando para pagamento...");
        // TODO: Integrar gateway de pagamento (Stripe, Mercado Pago, etc)
        setTimeout(() => {
            navigate("/dashboard/overview");
        }, 1500);
    };

    const features = [
        "Acesso ilimitado a 100+ mil produtos de afiliados",
        "Bot Telegram inteligente com AIDA persuasivo",
        "Dashboard profissional em tempo real",
        "Rotação automática de produtos (sem repetição)",
        "Envio automático 2x ao dia no Telegram",
        "Suporte prioritário via email",
        "Atualizações de produtos diárias",
        "Estatísticas completas de performance"
    ];

    return (
        <PageTransition>
            <div className="min-h-screen bg-slate-950 p-8">
                <div className="max-w-4xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-12">
                        <div className="inline-flex items-center gap-2 bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-full px-4 py-2 mb-6">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            <span className="text-sm font-semibold bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent">
                                OFERTA DE LANÇAMENTO - 90% OFF
                            </span>
                        </div>

                        <h1 className="text-5xl font-bold text-white mb-4">
                            Turbine suas <span className="bg-gradient-to-r from-indigo-500 to-purple-500 bg-clip-text text-transparent">vendas</span> hoje
                        </h1>
                        <p className="text-xl text-slate-400">
                            Acesso vitalício por um preço único de lançamento
                        </p>
                    </div>

                    {/* Pricing Card */}
                    <div className="relative">
                        {/* Badge de "Mais Popular" */}
                        <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
                            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-2 rounded-full text-sm font-semibold shadow-lg">
                                🔥 Oferta Limitada
                            </div>
                        </div>

                        <div className="bg-gradient-to-br from-slate-900 to-slate-950 border-2 border-indigo-500/50 rounded-2xl p-8 shadow-2xl shadow-indigo-500/20 relative overflow-hidden">
                            {/* Efeito de brilho */}
                            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 pointer-events-none"></div>

                            <div className="relative z-10">
                                {/* Preço */}
                                <div className="text-center mb-8">
                                    <div className="flex items-center justify-center gap-3 mb-4">
                                        <Bot className="w-12 h-12 text-indigo-500" />
                                        <h2 className="text-3xl font-bold text-white">AfiliadoBot Pro</h2>
                                    </div>

                                    <div className="flex items-baseline justify-center gap-2 mb-2">
                                        <span className="text-slate-500 line-through text-2xl">R$ 99,00</span>
                                        <span className="text-6xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
                                            R$ 9,90
                                        </span>
                                    </div>
                                    <p className="text-slate-400 text-sm">
                                        Pagamento único • Acesso vitalício • Sem mensalidades
                                    </p>
                                </div>

                                {/* Features */}
                                <div className="space-y-4 mb-8">
                                    {features.map((feature, index) => (
                                        <div key={index} className="flex items-start gap-3">
                                            <div className="mt-0.5 w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center flex-shrink-0">
                                                <Check className="w-3 h-3 text-green-400" />
                                            </div>
                                            <span className="text-slate-300">{feature}</span>
                                        </div>
                                    ))}
                                </div>

                                {/* Garantias */}
                                <div className="grid grid-cols-3 gap-4 mb-8 p-6 bg-slate-950/50 rounded-xl border border-slate-800">
                                    <div className="text-center">
                                        <Shield className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                                        <div className="text-xs text-slate-400">Pagamento</div>
                                        <div className="text-sm font-semibold text-white">Seguro</div>
                                    </div>
                                    <div className="text-center">
                                        <TrendingUp className="w-6 h-6 text-green-400 mx-auto mb-2" />
                                        <div className="text-xs text-slate-400">Atualizações</div>
                                        <div className="text-sm font-semibold text-white">Grátis</div>
                                    </div>
                                    <div className="text-center">
                                        <Zap className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
                                        <div className="text-xs text-slate-400">Ativação</div>
                                        <div className="text-sm font-semibold text-white">Imediata</div>
                                    </div>
                                </div>

                                {/* CTA Button */}
                                <button
                                    onClick={handleSubscribe}
                                    className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-indigo-500/50 hover:shadow-indigo-500/70 hover:scale-[1.02] active:scale-[0.98]"
                                >
                                    🚀 Assinar Agora por R$ 9,90
                                </button>

                                <p className="text-center text-xs text-slate-500 mt-4">
                                    Preço válido apenas para os primeiros 100 usuários
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Testimonial / Social Proof */}
                    <div className="mt-12 text-center">
                        <p className="text-slate-400 text-sm mb-4">
                            Junte-se a centenas de afiliados aumentando suas vendas
                        </p>
                        <div className="flex justify-center gap-2">
                            {[...Array(5)].map((_, i) => (
                                <div key={i} className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
                                    {String.fromCharCode(65 + i)}
                                </div>
                            ))}
                            <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 text-xs">
                                +95
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </PageTransition>
    );
};
