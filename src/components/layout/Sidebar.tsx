import { LayoutDashboard, Link as LinkIcon, Upload, Send, Zap, Settings, LogOut, Bot } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export const Sidebar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { logout } = useAuth();
    const activeTab = location.pathname.split('/dashboard/')[1] || 'overview';

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex-col hidden md:flex">
            <div className="h-16 flex items-center gap-2 px-6 border-b border-slate-200 dark:border-slate-800">
                <div className="w-6 h-6 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded flex items-center justify-center">
                    <Bot className="w-3 h-3 text-white" />
                </div>
                <span className="font-bold text-lg">AfiliadoBot</span>
            </div>

            <nav className="flex-1 p-4 space-y-1">
                <SidebarItem
                    icon={<LayoutDashboard size={20} />}
                    label="Visão Geral"
                    active={activeTab === 'overview'}
                    onClick={() => navigate('/dashboard/overview')}
                />
                <SidebarItem
                    icon={<LinkIcon size={20} />}
                    label="Produtos"
                    active={activeTab === 'products'}
                    onClick={() => navigate('/dashboard/products')}
                />
                <SidebarItem
                    icon={<Upload size={20} />}
                    label="Importação"
                    active={activeTab === 'import'}
                    onClick={() => navigate('/dashboard/import')}
                />
                <SidebarItem
                    icon={<Send size={20} />}
                    label="Telegram"
                    active={activeTab === 'telegram'}
                    onClick={() => navigate('/dashboard/telegram')}
                />
                <SidebarItem
                    icon={<Zap size={20} />}
                    label="Ferramentas"
                    active={activeTab === 'tools'}
                    onClick={() => navigate('/dashboard/tools')}
                    isNew
                />
                <SidebarItem
                    icon={<Settings size={20} />}
                    label="Configurações"
                    active={activeTab === 'settings'}
                    onClick={() => navigate('/dashboard/settings')}
                />
            </nav>

            <div className="p-4 border-t border-slate-200 dark:border-slate-800">
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 px-3 py-2 w-full text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg transition-colors text-sm font-medium"
                >
                    <LogOut size={18} />
                    Sair
                </button>
            </div>
        </aside>
    );
};

const SidebarItem = ({ icon, label, active, onClick, isNew }: any) => (
    <button
        onClick={onClick}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${active
                ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
    >
        {icon}
        <span>{label}</span>
        {isNew && (
            <span className="ml-auto text-[10px] font-bold uppercase tracking-wider bg-gradient-to-r from-pink-500 to-rose-500 text-white px-1.5 py-0.5 rounded-full">
                New
            </span>
        )}
    </button>
);
