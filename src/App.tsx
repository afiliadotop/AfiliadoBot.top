import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider } from "./context/AuthContext";
import { ErrorBoundary } from "./components/ErrorBoundary";

import { PrivateRoute } from "./components/layout/PrivateRoute";
import { AdminRoute } from "./components/layout/AdminRoute";

// Loading fallback component
const PageLoader = () => (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
            <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-slate-400">Carregando...</p>
        </div>
    </div>
);

// Lazy loaded pages - code splitting by route
const LandingPage = lazy(() => import('./pages/LandingPage').then(m => ({ default: m.LandingPage })));
const Login = lazy(() => import('./pages/Login').then(m => ({ default: m.Login })));
const Register = lazy(() => import('./pages/Register').then(m => ({ default: m.Register })));
const ClientDashboard = lazy(() => import('./components/client/ClientDashboard').then(m => ({ default: m.ClientDashboard })));
const DashboardLayout = lazy(() => import('./components/layout/DashboardLayout').then(m => ({ default: m.DashboardLayout })));
const Overview = lazy(() => import('./components/dashboard/Overview').then(m => ({ default: m.Overview })));
const Products = lazy(() => import('./components/dashboard/Products').then(m => ({ default: m.Products })));

// Shopee pages
const ShopeeProducts = lazy(() => import('./pages/ShopeeProducts').then(m => ({ default: m.ShopeeProducts })));
const ShopeeAdmin = lazy(() => import('./pages/ShopeeAdmin').then(m => ({ default: m.ShopeeAdmin })));
const ShopeeFavorites = lazy(() => import('./pages/ShopeeFavorites').then(m => ({ default: m.ShopeeFavorites })));

// SaaS pages
const Pricing = lazy(() => import('./pages/Pricing').then(m => ({ default: m.Pricing })));
const Profile = lazy(() => import('./pages/Profile').then(m => ({ default: m.Profile })));

// Placeholders for components not yet extracted
const Placeholder = ({ title }: { title: string }) => (
    <div className="flex items-center justify-center h-64 bg-slate-50 dark:bg-slate-900 rounded-xl border border-dashed border-slate-300 dark:border-slate-800 text-slate-400">
        Em breve: {title}
    </div>
);

function App() {
    return (
        <ErrorBoundary>
            <Router>
                <AuthProvider>
                    <div className="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen font-sans">
                        <Toaster position="top-right" richColors />

                        <Suspense fallback={<PageLoader />}>
                            <Routes>
                                <Route path="/" element={<LandingPage />} />
                                <Route path="/login" element={<Login />} />
                                <Route path="/register" element={<Register />} />
                                <Route path="/pricing" element={<Pricing />} />

                                {/* Client Route */}
                                <Route path="/client" element={<PrivateRoute />}>
                                    <Route index element={<ClientDashboard />} />
                                </Route>

                                {/* Admin Route */}
                                <Route path="/dashboard" element={<AdminRoute />}>
                                    <Route element={<DashboardLayout />}>
                                        <Route index element={<Navigate to="/dashboard/overview" replace />} />
                                        <Route path="overview" element={<Overview />} />
                                        <Route path="products" element={<Products />} />
                                        <Route path="import" element={<Placeholder title="Importação de CSV" />} />
                                        <Route path="telegram" element={<Placeholder title="Automação Telegram" />} />
                                        <Route path="tools" element={<Placeholder title="Ferramentas IA" />} />
                                        <Route path="settings" element={<Placeholder title="Configurações" />} />
                                        <Route path="shopee" element={<ShopeeAdmin />} />
                                        <Route path="profile" element={<Profile />} />
                                    </Route>
                                </Route>

                                {/* Shopee Public Route */}
                                <Route path="/shopee" element={<PrivateRoute />}>
                                    <Route index element={<ShopeeProducts />} />
                                </Route>

                                <Route path="*" element={<Navigate to="/" replace />} />
                            </Routes>
                        </Suspense>
                    </div>
                </AuthProvider>
            </Router>
        </ErrorBoundary>
    );
}

export default App;
