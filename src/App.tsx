import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider } from "./context/AuthContext";
import { PrivateRoute } from "./components/layout/PrivateRoute";
import { LandingPage } from "./pages/LandingPage";
import { Login } from "./pages/Login";
import { DashboardLayout } from "./components/layout/DashboardLayout";
import { Overview } from "./components/dashboard/Overview";
import { Products } from "./components/dashboard/Products";

// Placeholders for components not yet extracted
const Placeholder = ({ title }: { title: string }) => (
    <div className="flex items-center justify-center h-64 bg-slate-50 dark:bg-slate-900 rounded-xl border border-dashed border-slate-300 dark:border-slate-800 text-slate-400">
        Em breve: {title}
    </div>
);

function App() {
    return (
        <Router>
            <AuthProvider>
                <div className="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen font-sans">
                    <Toaster position="top-right" richColors />
                    <Routes>
                        <Route path="/" element={<LandingPage />} />
                        <Route path="/login" element={<Login />} />

                        <Route path="/dashboard" element={<PrivateRoute />}>
                            <Route element={<DashboardLayout />}>
                                <Route index element={<Navigate to="/dashboard/overview" replace />} />
                                <Route path="overview" element={<Overview />} />
                                <Route path="products" element={<Products />} />
                                <Route path="import" element={<Placeholder title="Importação de CSV" />} />
                                <Route path="telegram" element={<Placeholder title="Automação Telegram" />} />
                                <Route path="tools" element={<Placeholder title="Ferramentas IA" />} />
                                <Route path="settings" element={<Placeholder title="Configurações" />} />
                            </Route>
                        </Route>

                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </div>
            </AuthProvider>
        </Router>
    );
}

export default App;
