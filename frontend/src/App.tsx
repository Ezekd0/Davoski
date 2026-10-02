import { Suspense, lazy, Component, type ReactNode, type ErrorInfo } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import Layout from './components/Layout';
import Login from './pages/Login';
import { Loading, ErrorState } from './components/UI';
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Analysis = lazy(() => import('./pages/Analysis'));
const Threats = lazy(() => import('./pages/Threats').then(m => ({ default: m.Threats })));
const ThreatDetail = lazy(() => import('./pages/Threats').then(m => ({ default: m.ThreatDetail })));
const Incidents = lazy(() => import('./pages/Incidents').then(m => ({ default: m.Incidents })));
const IncidentDetail = lazy(() => import('./pages/Incidents').then(m => ({ default: m.IncidentDetail })));
const Alerts = lazy(() => import('./pages/Alerts'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Settings = lazy(() => import('./pages/Workspace').then(m => ({ default: m.Settings })));
const Audit = lazy(() => import('./pages/Workspace').then(m => ({ default: m.Audit })));
const Users = lazy(() => import('./pages/Workspace').then(m => ({ default: m.Users })));
class ErrorBoundary extends Component<{
    children: ReactNode;
}, {
    failed: boolean;
}> {
    state = { failed: false };
    static getDerivedStateFromError() { return { failed: true }; }
    componentDidCatch(error: Error, _info: ErrorInfo) { console.error('UI rendering failed', error.message); }
    render() { return this.state.failed ? <div className="fatal-error"><ErrorState error="This screen could not load. Reload the application to retry." retry={() => window.location.reload()}/></div> : this.props.children; }
}
function AppRoutes() { const { user, loading } = useAuth(); if (loading)
    return <Loading />; return <Suspense fallback={<Loading />}><Routes>{!user ? <><Route path="/login" element={<Login />}/><Route path="*" element={<Navigate to="/login" replace/>}/></> : <><Route path="/login" element={<Navigate to="/" replace/>}/><Route element={<Layout />}><Route index element={<Dashboard />}/><Route path="analysis" element={<Analysis />}/><Route path="threats" element={<Threats />}/><Route path="threats/:id" element={<ThreatDetail />}/><Route path="incidents" element={<Incidents />}/><Route path="incidents/:id" element={<IncidentDetail />}/><Route path="alerts" element={<Alerts />}/><Route path="analytics" element={<Analytics />}/><Route path="audit" element={<Audit />}/><Route path="settings" element={<Settings />}/><Route path="users" element={user.role === 'ADMIN' ? <Users /> : <Navigate to="/" replace/>}/><Route path="*" element={<div className="empty"><h1>Page not found</h1><Link className="btn primary" to="/">Return to dashboard</Link></div>}/></Route></>}</Routes></Suspense>; }
export default function App() { return <ErrorBoundary><BrowserRouter><AuthProvider><AppRoutes /></AuthProvider></BrowserRouter></ErrorBoundary>; }
