import React, { useState, useEffect } from "react";
import { User, Mail, Shield, Calendar, CreditCard, Loader2 } from "lucide-react";
import { PageTransition } from "../components/layout/PageTransition";
import { useAuth } from "../hooks/useAuth";
import { api } from "../services/api";
import { toast } from "sonner";

export const Profile = () => {
    const { user } = useAuth();
    const [isLoading, setIsLoading] = useState(true);
    const [profile, setProfile] = useState<any>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [name, setName] = useState("");

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        setIsLoading(true);
        try {
            const data = await api.get(`/api/users/profile`);
            if (data) {
                setProfile(data);
                setName(data.name || user?.name || "");
            }
        } catch (error) {
            console.error("Error loading profile:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSave = async () => {
        try {
            const updated = await api.put(`/api/users/profile`, { name });
            if (updated) {
                toast.success("Perfil atualizado com sucesso!");
                setProfile({ ...profile, name });
                setIsEditing(false);
            }
        } catch (error) {
            toast.error("Erro ao atualizar perfil");
        }
    };

    const getSubscriptionBadge = (status: string) => {
        const badges: Record<string, { bg: string; text: string; label: string }> = {
            active: { bg: "bg-green-500/20", text: "text-green-400", label: "✓ Ativa" },
            trial: { bg: "bg-yellow-500/20", text: "text-yellow-400", label: "⏱ Trial" },
            expired: { bg: "bg-red-500/20", text: "text-red-400", label: "✗ Expirada" }
        };
        const badge = badges[status] || badges.trial;
        return (
            <span className={`${badge.bg} ${badge.text} px-3 py-1 rounded-full text-sm font-semibold`}>
                {badge.label}
            </span>
        );
    };

    if (isLoading) {
        return (
            <PageTransition>
                <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                    <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                </div>
            </PageTransition>
        );
    }

    return (
        <PageTransition>
            <div className="min-h-screen bg-slate-950 p-8">
                <div className="max-w-4xl mx-auto">
                    <h1 className="text-3xl font-bold text-white mb-8">Meu Perfil</h1>

                    {/* Profile Card */}
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 mb-6">
                        <div className="flex items-center gap-6 mb-8">
                            {/* Avatar */}
                            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white text-3xl font-bold">
                                {(name || user?.name || "U").charAt(0).toUpperCase()}
                            </div>

                            {/* User Info */}
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                    {isEditing ? (
                                        <input
                                            type="text"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                            className="bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white text-2xl font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                        />
                                    ) : (
                                        <h2 className="text-2xl font-bold text-white">{name || user?.name || "Usuário"}</h2>
                                    )}
                                </div>
                                <p className="text-slate-400 flex items-center gap-2">
                                    <Mail className="w-4 h-4" />
                                    {user?.email}
                                </p>
                            </div>

                            {/* Edit Button */}
                            {isEditing ? (
                                <div className="flex gap-2">
                                    <button
                                        onClick={handleSave}
                                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg transition-colors"
                                    >
                                        Salvar
                                    </button>
                                    <button
                                        onClick={() => {
                                            setIsEditing(false);
                                            setName(profile?.name || user?.name || "");
                                        }}
                                        className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg transition-colors"
                                    >
                                        Cancelar
                                    </button>
                                </div>
                            ) : (
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg transition-colors"
                                >
                                    Editar
                                </button>
                            )}
                        </div>

                        {/* Info Grid */}
                        <div className="grid grid-cols-2 gap-6">
                            <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
                                <div className="flex items-center gap-3 mb-2">
                                    <Shield className="w-5 h-5 text-indigo-400" />
                                    <span className="text-slate-400 text-sm">Plano</span>
                                </div>
                                <div className="text-white font-semibold mb-2">AfiliadoBot Pro</div>
                                {getSubscriptionBadge(profile?.subscription_status || user?.subscription_status || "trial")}
                            </div>

                            <div className="bg-slate-950 border border-slate-800 rounded-xl p-6">
                                <div className="flex items-center gap-3 mb-2">
                                    <Calendar className="w-5 h-5 text-purple-400" />
                                    <span className="text-slate-400 text-sm">Membro desde</span>
                                </div>
                                <div className="text-white font-semibold">
                                    {profile?.created_at
                                        ? new Date(profile.created_at).toLocaleDateString("pt-BR")
                                        : "Janeiro 2026"}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Upgrade Card (if not active) */}
                    {(profile?.subscription_status !== "active" && user?.subscription_status !== "active") && (
                        <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/30 rounded-2xl p-8">
                            <div className="flex items-center gap-4 mb-4">
                                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
                                    <CreditCard className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-white">Upgrade para Pro</h3>
                                    <p className="text-slate-400">Apenas R$ 9,90 - Oferta de lançamento</p>
                                </div>
                            </div>
                            <button
                                onClick={() => (window.location.href = "/pricing")}
                                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 rounded-lg transition-all"
                            >
                                Ver Planos
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </PageTransition>
    );
};
