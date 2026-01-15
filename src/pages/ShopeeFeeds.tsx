import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';
import { PageTransition } from '../components/layout/PageTransition';
import {
    Activity, Play, CheckCircle, AlertTriangle, Clock,
    Plus, Trash2, Loader2, Database, ExternalLink
} from 'lucide-react';
import { Navigate } from 'react-router-dom';

interface Feed {
    id: string;
    name: string;
    url: string;
    status: 'success' | 'failed' | 'running' | 'warning' | null;
    last_run_at: string | null;
    created_at: string;
    schedule_cron: string;
    is_active: boolean;
}

export const ShopeeFeeds = () => {
    const { user } = useAuth();
    const [feeds, setFeeds] = useState<Feed[]>([]);
    const [loading, setLoading] = useState(true);
    const [runningId, setRunningId] = useState<string | null>(null);
    const [showAddModal, setShowAddModal] = useState(false);

    // New Feed State
    const [newFeedName, setNewFeedName] = useState('');
    const [newFeedUrl, setNewFeedUrl] = useState('');

    if (user?.role !== 'admin') {
        return <Navigate to="/shopee" replace />;
    }

    useEffect(() => {
        loadFeeds();
    }, []);

    const loadFeeds = async () => {
        setLoading(true);
        try {
            const data = await api.get<Feed[]>('/feeds');
            setFeeds(data || []);
        } catch (error) {
            console.error("Error loading feeds:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleRunFeed = async (feedId: string) => {
        setRunningId(feedId);
        try {
            await api.post(`/feeds/${feedId}/run`);
            // Optimistic update
            setFeeds(prev => prev.map(f =>
                f.id === feedId ? { ...f, status: 'running' } : f
            ));
            alert('Processamento iniciado em segundo plano!');
        } catch (error: any) {
            alert(`Erro ao iniciar: ${error.message}`);
        } finally {
            // Reload after a delay to hopefully catch status change
            setTimeout(loadFeeds, 2000);
            setRunningId(null);
        }
    };

    const handleAddFeed = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/feeds', {
                name: newFeedName,
                url: newFeedUrl,
                store_id: 1 // Default to Shopee
            });
            setShowAddModal(false);
            setNewFeedName('');
            setNewFeedUrl('');
            loadFeeds();
        } catch (error: any) {
            alert(`Erro ao criar feed: ${error.message}`);
        }
    };

    const handleDeleteFeed = async (feedId: string) => {
        if (!confirm('Tem certeza que deseja excluir este feed?')) return;
        try {
            await api.delete(`/feeds/${feedId}`);
            loadFeeds();
        } catch (error: any) {
            alert(`Erro ao excluir: ${error.message}`);
        }
    };

    const getStatusBadge = (status: string | null) => {
        switch (status) {
            case 'success':
                return <span className="px-2 py-1 bg-green-500/10 text-green-400 rounded-full text-xs flex items-center gap-1 border border-green-500/20"><CheckCircle className="w-3 h-3" /> Sucesso</span>;
            case 'failed':
                return <span className="px-2 py-1 bg-red-500/10 text-red-400 rounded-full text-xs flex items-center gap-1 border border-red-500/20"><AlertTriangle className="w-3 h-3" /> Falha</span>;
            case 'running':
                return <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded-full text-xs flex items-center gap-1 border border-blue-500/20"><Loader2 className="w-3 h-3 animate-spin" /> Processando</span>;
            case 'warning':
                return <span className="px-2 py-1 bg-yellow-500/10 text-yellow-400 rounded-full text-xs flex items-center gap-1 border border-yellow-500/20"><AlertTriangle className="w-3 h-3" /> Aviso</span>;
            default:
                return <span className="px-2 py-1 bg-slate-500/10 text-slate-400 rounded-full text-xs border border-slate-500/20">Aguardando</span>;
        }
    };

    return (
        <PageTransition>
            <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
                <div className="max-w-7xl mx-auto space-y-8">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-400 to-orange-600 bg-clip-text text-transparent flex items-center gap-3">
                                <Database className="w-8 h-8 text-orange-500" />
                                Status dos Feeds
                            </h1>
                            <p className="text-slate-400 mt-1">
                                Gerencie a importação automática de produtos via CSV
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={loadFeeds}
                                className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg hover:bg-slate-800 transition-colors"
                            >
                                <Activity className="w-4 h-4" />
                                Atualizar
                            </button>
                            <button
                                onClick={() => setShowAddModal(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-orange-600 rounded-lg hover:bg-orange-700 transition-colors"
                            >
                                <Plus className="w-4 h-4" />
                                Novo Feed
                            </button>
                        </div>
                    </div>

                    {/* Feed List */}
                    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-slate-950/50 border-b border-slate-800">
                                    <tr>
                                        <th className="p-4 text-sm font-medium text-slate-400">Nome do Feed</th>
                                        <th className="p-4 text-sm font-medium text-slate-400">Status</th>
                                        <th className="p-4 text-sm font-medium text-slate-400">Última Execução</th>
                                        <th className="p-4 text-sm font-medium text-slate-400">Cronograma</th>
                                        <th className="p-4 text-sm font-medium text-slate-400 text-right">Ações</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800">
                                    {loading ? (
                                        <tr>
                                            <td colSpan={5} className="p-8 text-center text-slate-500">
                                                <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                                                Carregando feeds...
                                            </td>
                                        </tr>
                                    ) : feeds.length === 0 ? (
                                        <tr>
                                            <td colSpan={5} className="p-8 text-center text-slate-500">
                                                Nenhum feed configurado.
                                            </td>
                                        </tr>
                                    ) : (
                                        feeds.map((feed) => (
                                            <tr key={feed.id} className="hover:bg-slate-800/50 transition-colors">
                                                <td className="p-4">
                                                    <div className="font-medium text-slate-200">{feed.name}</div>
                                                    <a href={feed.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:underline flex items-center gap-1 truncate max-w-[300px]">
                                                        {feed.url} <ExternalLink className="w-3 h-3" />
                                                    </a>
                                                </td>
                                                <td className="p-4">
                                                    {getStatusBadge(feed.status)}
                                                </td>
                                                <td className="p-4 text-sm text-slate-400">
                                                    <div className="flex items-center gap-2">
                                                        <Clock className="w-4 h-4" />
                                                        {feed.last_run_at
                                                            ? new Date(feed.last_run_at).toLocaleString('pt-BR')
                                                            : 'Nunca executado'
                                                        }
                                                    </div>
                                                </td>
                                                <td className="p-4 text-sm text-slate-400 font-mono">
                                                    {feed.schedule_cron}
                                                </td>
                                                <td className="p-4 text-right">
                                                    <div className="flex items-center justify-end gap-2">
                                                        <button
                                                            onClick={() => handleRunFeed(feed.id)}
                                                            disabled={runningId === feed.id || feed.status === 'running'}
                                                            className={`p-2 rounded-lg transition-colors border ${feed.status === 'running'
                                                                ? 'bg-slate-800 border-slate-700 text-slate-500 cursor-not-allowed'
                                                                : 'bg-green-500/10 border-green-500/20 text-green-400 hover:bg-green-500/20'
                                                                }`}
                                                            title="Processar Agora"
                                                        >
                                                            {runningId === feed.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                                                        </button>
                                                        <button
                                                            onClick={() => handleDeleteFeed(feed.id)}
                                                            className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition-colors"
                                                            title="Excluir"
                                                        >
                                                            <Trash2 className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                {/* Add Feed Modal */}
                {showAddModal && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
                            <h2 className="text-xl font-bold mb-4">Novo Feed de Produtos</h2>
                            <form onSubmit={handleAddFeed} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1 text-slate-400">Nome do Feed</label>
                                    <input
                                        type="text"
                                        required
                                        value={newFeedName}
                                        onChange={e => setNewFeedName(e.target.value)}
                                        className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-lg focus:ring-2 focus:ring-orange-500 outline-none"
                                        placeholder="Ex: Shopee Ofertas BR"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1 text-slate-400">URL do CSV</label>
                                    <input
                                        type="url"
                                        required
                                        value={newFeedUrl}
                                        onChange={e => setNewFeedUrl(e.target.value)}
                                        className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-lg focus:ring-2 focus:ring-orange-500 outline-none"
                                        placeholder="https://..."
                                    />
                                </div>
                                <div className="flex justify-end gap-3 mt-6">
                                    <button
                                        type="button"
                                        onClick={() => setShowAddModal(false)}
                                        className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
                                    >
                                        Cancelar
                                    </button>
                                    <button
                                        type="submit"
                                        className="px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg font-medium transition-colors"
                                    >
                                        Adicionar Feed
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </div>
        </PageTransition>
    );
};
