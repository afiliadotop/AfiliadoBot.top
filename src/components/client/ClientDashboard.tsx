import React from "react";
import { useAuth } from "../../hooks/useAuth";
import { PageTransition } from "../layout/PageTransition";
import { Package, LogOut, ShoppingBag } from "lucide-react";

export const ClientDashboard = () => {
    const { user, logout } = useAuth();

    return (
        <PageTransition>
            <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
                <div className="max-w-6xl mx-auto">
                    <header className="flex items-center justify-between mb-10 pb-6 border-b border-slate-800">
                        <div>
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
                                Área do Cliente
                            </h1>
                            <p className="text-slate-400 mt-1">Bem-vindo, {user?.name}</p>
                        </div>
                        <button
                            onClick={logout}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 transition-colors text-slate-300"
                        >
                            <LogOut className="w-4 h-4" />
                            Sair
                        </button>
                    </header>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                            <div className="w-12 h-12 bg-indigo-500/10 rounded-lg flex items-center justify-center mb-4">
                                <ShoppingBag className="w-6 h-6 text-indigo-400" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">Produtos Disponíveis</h3>
                            <p className="text-slate-400 text-sm">
                                Visualize os produtos disponíveis para afiliação.
                            </p>
                        </div>

                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 opacity-50">
                            <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center mb-4">
                                <Package className="w-6 h-6 text-emerald-400" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">Meus Pedidos</h3>
                            <p className="text-slate-400 text-sm">
                                Em breve disponível.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </PageTransition>
    );
};
