import React, { useState, useEffect } from 'react';
import { Shield, RefreshCw, Send, Check, X, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { api } from '../services/api';
import { PageTransition } from '../components/layout/PageTransition';

export const TelegramSettings = () => {
    const [botToken, setBotToken] = useState('');
    const [groupChatId, setGroupChatId] = useState('');
    const [loading, setLoading] = useState(false);
    const [testing, setTesting] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [currentSettings, setCurrentSettings] = useState<any>(null);
    const [status, setStatus] = useState<any>(null);

    useEffect(() => {
        fetchSettings();
        fetchStatus();
    }, []);

    const fetchSettings = async () => {
        try {
            const response = await api.get('/telegram/settings');
            setCurrentSettings(response.data.settings);
            setGroupChatId(response.data.settings?.group_chat_id || '');
        } catch (error: any) {
            console.error('Error loading settings:', error);
            toast.error('Erro ao carregar configurações');
        }
    };

    const fetchStatus = async () => {
        try {
            const response = await api.get('/telegram/settings/status');
            setStatus(response.data.status);
        } catch (error: any) {
            console.error('Error loading status:', error);
        }
    };

    const handleRefreshCache = async () => {
        setRefreshing(true);
        try {
            await api.post('/telegram/settings/refresh');
            toast.success('Cache atualizado!');
            fetchSettings();
            fetchStatus();
        } catch (error: any) {
            toast.error('Erro ao atualizar cache');
        } finally {
            setRefreshing(false);
        }
    };

    const handleTest = async () => {
        if (!botToken || !groupChatId) {
            toast.error('Preencha todos os campos para testar');
            return;
        }

        setTesting(true);
        try {
            const response = await api.post('/telegram/settings/test', {
                bot_token: botToken,
                group_chat_id: groupChatId
            });

            toast.success(`✅ ${response.data.message}`);
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Erro ao testar conexão');
        } finally {
            setTesting(false);
        }
    };

    const handleSave = async () => {
        if (!botToken || !groupChatId) {
            toast.error('Preencha todos os campos');
            return;
        }

        setLoading(true);
        try {
            await api.put('/telegram/settings', {
                bot_token: botToken,
                group_chat_id: groupChatId
            });

            toast.success('✅ Configurações salvas com sucesso!');
            setBotToken('');
            fetchSettings();
            fetchStatus();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Erro ao salvar configurações');
        } finally {
            setLoading(false);
        }
    };

    return (
        <PageTransition>
            <div className="max-w-4xl mx-auto p-6 space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Shield className="text-indigo-600 dark:text-indigo-400" size={32} />
                        <div>
                            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                                Configurações do Telegram
                            </h1>
                            <p className="text-sm text-slate-500 dark:text-slate-400">
                                Gerencie o bot e grupo de mensagens
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={handleRefreshCache}
                        disabled={refreshing}
                        className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
                    >
                        <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
                        Atualizar Cache
                    </button>
                </div>

                {/* Status Card */}
                {status && (
                    <div className={`p-4 rounded-xl border ${status.is_configured
                        ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                        : 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800'
                        }`}>
                        <div className="flex items-start gap-3">
                            {status.is_configured ? (
                                <Check className="text-green-600 dark:text-green-400" size={20} />
                            ) : (
                                <AlertCircle className="text-orange-600 dark:text-orange-400" size={20} />
                            )}
                            <div className="flex-1">
                                <h3 className={`font-semibold ${status.is_configured
                                    ? 'text-green-900 dark:text-green-100'
                                    : 'text-orange-900 dark:text-orange-100'
                                    }`}>
                                    {status.is_configured ? '✅ Configurado e Ativo' : '⚠️ Configuração Incompleta'}
                                </h3>
                                <div className="mt-2 text-sm space-y-1">
                                    <p className="text-slate-600 dark:text-slate-400">
                                        <strong>Bot Token:</strong> {status.has_bot_token ? '✓ Configurado' : '✗ Não configurado'}
                                    </p>
                                    <p className="text-slate-600 dark:text-slate-400">
                                        <strong>Group ID:</strong> {status.has_group_chat_id ? '✓ Configurado' : '✗ Não configurado'}
                                    </p>
                                    {status.test_bot_username && (
                                        <p className="text-slate-600 dark:text-slate-400">
                                            <strong>Bot Testado:</strong> @{status.test_bot_username}
                                        </p>
                                    )}
                                    {status.cache_age_seconds !== null && (
                                        <p className="text-slate-600 dark:text-slate-400">
                                            <strong>Cache:</strong> {status.cache_age_seconds}s (TTL: 5min)
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Current Config */}
                {currentSettings && (currentSettings.bot_token_masked || currentSettings.group_chat_id) && (
                    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
                        <h3 className="font-semibold text-lg mb-4 text-slate-900 dark:text-slate-100">
                            Configuração Atual
                        </h3>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-slate-600 dark:text-slate-400">Token:</span>
                                <span className="font-mono text-slate-900 dark:text-slate-100">
                                    {currentSettings.bot_token_masked || 'Não configurado'}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-600 dark:text-slate-400">Group ID:</span>
                                <span className="font-mono text-slate-900 dark:text-slate-100">
                                    {currentSettings.group_chat_id || 'Não configurado'}
                                </span>
                            </div>
                            {currentSettings.updated_at && (
                                <div className="flex justify-between">
                                    <span className="text-slate-600 dark:text-slate-400">Última atualização:</span>
                                    <span className="text-slate-900 dark:text-slate-100">
                                        {new Date(currentSettings.updated_at).toLocaleString('pt-BR')}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Update Form */}
                <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
                    <h3 className="font-semibold text-lg mb-4 text-slate-900 dark:text-slate-100">
                        Atualizar Configurações
                    </h3>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2 text-slate-700 dark:text-slate-300">
                                Bot Token
                            </label>
                            <input
                                type="password"
                                value={botToken}
                                onChange={(e) => setBotToken(e.target.value)}
                                placeholder="1234567890:AAF_xxxxxx..."
                                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900 dark:text-slate-100"
                            />
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                Obtido do @BotFather no Telegram
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2 text-slate-700 dark:text-slate-300">
                                Group Chat ID
                            </label>
                            <input
                                type="text"
                                value={groupChatId}
                                onChange={(e) => setGroupChatId(e.target.value)}
                                placeholder="-1001234567890"
                                className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-sm outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900 dark:text-slate-100"
                            />
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                ID do grupo/canal onde o bot enviará mensagens (deve começar com -)
                            </p>
                        </div>

                        <div className="flex gap-3 pt-2">
                            <button
                                onClick={handleTest}
                                disabled={testing || !botToken || !groupChatId}
                                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <Send size={16} />
                                {testing ? 'Testando...' : 'Testar Conexão'}
                            </button>

                            <button
                                onClick={handleSave}
                                disabled={loading || !botToken || !groupChatId}
                                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Salvando...' : '💾 Salvar Configurações'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Help */}
                <div className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-xl p-4">
                    <h4 className="font-semibold text-indigo-900 dark:text-indigo-100 mb-2">
                        📖 Como Configurar
                    </h4>
                    <ol className="text-sm text-indigo-800 dark:text-indigo-200 space-y-1 list-decimal list-inside">
                        <li>Crie um bot no @BotFather e copie o token</li>
                        <li>Adicione o bot ao seu grupo/canal</li>
                        <li>Use @userinfobot para obter o Group Chat ID</li>
                        <li>Cole as informações acima e clique em "Testar Conexão"</li>
                        <li>Se o teste passar, clique em "Salvar Configurações"</li>
                    </ol>
                </div>
            </div>
        </PageTransition>
    );
};

export default TelegramSettings;
