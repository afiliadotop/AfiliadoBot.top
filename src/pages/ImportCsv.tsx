import React, { useState } from 'react';
import { api } from '../services/api';
import { toast } from 'sonner';
import { Upload, FileType, CheckCircle, AlertCircle, RefreshCw, Send } from 'lucide-react';

const ImportCsv = () => {
    const [file, setFile] = useState<File | null>(null);
    const [store, setStore] = useState('shopee');
    const [loading, setLoading] = useState(false);
    const [sendToTelegram, setSendToTelegram] = useState(false);
    const [uploadStats, setUploadStats] = useState<any>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setUploadStats(null);
        }
    };

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!file) {
            toast.error('Por favor, selecione um arquivo CSV');
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('store', store);
        formData.append('send_to_telegram', String(sendToTelegram)); // Converte booleano para string

        try {
            toast.info('Iniciando upload... Isso pode levar alguns minutos.');

            await api.post('/import/csv', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            toast.success('Importação iniciada em segundo plano! Você será notificado quando terminar.');
            setFile(null);
            setUploadStats({ status: 'processing', message: 'Processando em background...' });

        } catch (error) {
            console.error(error);
            toast.error('Erro ao enviar arquivo.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                    Importação de Produtos
                </h1>
                <p className="text-gray-500 dark:text-gray-400 mt-1">
                    Carregue produtos em massa via CSV e envie para o Telegram
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Card de Upload */}
                <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                    <form onSubmit={handleUpload} className="space-y-6">
                        {/* Seleção de Loja */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Loja de Origem
                            </label>
                            <select
                                value={store}
                                onChange={(e) => setStore(e.target.value)}
                                className="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                            >
                                <option value="shopee">Shopee</option>
                                <option value="aliexpress">AliExpress</option>
                                <option value="amazon">Amazon</option>
                                <option value="magalu">Magazine Luiza</option>
                                <option value="shein">Shein</option>
                            </select>
                        </div>

                        {/* Área de Drop */}
                        <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl p-8 text-center hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                            <input
                                type="file"
                                accept=".csv"
                                onChange={handleFileChange}
                                className="hidden"
                                id="file-upload"
                            />
                            <label
                                htmlFor="file-upload"
                                className="cursor-pointer flex flex-col items-center justify-center space-y-3"
                            >
                                <div className="p-4 bg-indigo-50 dark:bg-indigo-900/30 rounded-full text-indigo-600 dark:text-indigo-400">
                                    <Upload className="w-8 h-8" />
                                </div>
                                <div className="text-sm">
                                    <span className="font-semibold text-indigo-600 dark:text-indigo-400">
                                        Clique para upload
                                    </span>
                                    {' '}ou arraste e solte
                                </div>
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                    Apenas arquivos CSV (max. 10MB)
                                </p>
                            </label>
                        </div>

                        {/* Arquivo Selecionado */}
                        {file && (
                            <div className="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                                <FileType className="w-5 h-5 text-indigo-500" />
                                <span className="text-sm font-medium truncate flex-1">
                                    {file.name}
                                </span>
                                <span className="text-xs text-gray-500">
                                    {(file.size / 1024).toFixed(1)} KB
                                </span>
                            </div>
                        )}

                        {/* Opções Extras */}
                        <div className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                id="telegram-check"
                                checked={sendToTelegram}
                                onChange={(e) => setSendToTelegram(e.target.checked)}
                                className="w-4 h-4 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 dark:focus:ring-indigo-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                            />
                            <label htmlFor="telegram-check" className="text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
                                <Send className="w-4 h-4 text-blue-500" />
                                Enviar produtos para o Telegram após importar
                            </label>
                        </div>
                        {sendToTelegram && (
                            <div className="text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 p-3 rounded-lg flex items-start gap-2">
                                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                                <span>
                                    Atenção: O envio para o Telegram pode demorar. O sistema enviará os primeiros 5 produtos de cada lote para evitar bloqueios.
                                </span>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading || !file}
                            className={`w-full py-2.5 px-4 rounded-lg text-white font-medium flex items-center justify-center space-x-2 transition-all ${loading || !file
                                    ? 'bg-gray-400 cursor-not-allowed'
                                    : 'bg-indigo-600 hover:bg-indigo-700 shadow-lg hover:shadow-indigo-500/30'
                                }`}
                        >
                            {loading ? (
                                <>
                                    <RefreshCw className="w-5 h-5 animate-spin" />
                                    <span>Processando...</span>
                                </>
                            ) : (
                                <>
                                    <Upload className="w-5 h-5" />
                                    <span>Iniciar Importação</span>
                                </>
                            )}
                        </button>
                    </form>
                </div>

                {/* Card de Instruções */}
                <div className="space-y-6">
                    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
                        <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                            <AlertCircle className="w-5 h-5 text-indigo-500" />
                            Instruções
                        </h3>
                        <ul className="space-y-3 text-sm text-gray-600 dark:text-gray-400 list-disc list-inside">
                            <li>O arquivo deve estar no formato <strong>.CSV</strong></li>
                            <li>
                                Colunas obrigatórias:
                                <code className="mx-1 px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-indigo-600 dark:text-indigo-400">
                                    name
                                </code>
                                e
                                <code className="mx-1 px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-indigo-600 dark:text-indigo-400">
                                    link
                                </code>
                            </li>
                            <li>Colunas opcionais: price, original_price, image, category</li>
                            <li>A importação roda em segundo plano para não travar o navegador</li>
                            <li>Verifique o canal do Telegram para confirmar o envio</li>
                        </ul>
                    </div>

                    {uploadStats && (
                        <div className="bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800 p-6">
                            <div className="flex items-center gap-3 text-green-700 dark:text-green-400 font-medium">
                                <CheckCircle className="w-6 h-6" />
                                <span>{uploadStats.message}</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ImportCsv;
