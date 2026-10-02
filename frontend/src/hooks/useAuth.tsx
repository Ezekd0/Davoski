import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { api, post, setTokens, clearTokens, getRefresh } from '../services/api';
import type { User } from '../types';
interface Auth {
    user: User | null;
    loading: boolean;
    error: string;
    login: (username: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    retry: () => void;
}
const Context = createContext<Auth | null>(null);
export function AuthProvider({ children }: {
    children: ReactNode;
}) {
    const [user, setUser] = useState<User | null>(null), [loading, setLoading] = useState(true), [error, setError] = useState(''), [attempt, setAttempt] = useState(0);
    useEffect(() => { let active = true; if (!getRefresh()) {
        setLoading(false);
        return;
    } setLoading(true); setError(''); api<User>('/auth/profile/').then(u => { if (active)
        setUser(u); }).catch(e => { if (active)
        setError(e.message); }).finally(() => { if (active)
        setLoading(false); }); return () => { active = false; }; }, [attempt]);
    useEffect(() => { const expired = () => { setUser(null); setError('Your session expired. Please sign in again.'); }; window.addEventListener('auth-expired', expired); return () => window.removeEventListener('auth-expired', expired); }, []);
    async function login(username: string, password: string) { const tokens = await post<{
        access: string;
        refresh: string;
    }>('/auth/login/', { username, password }); setTokens(tokens.access, tokens.refresh); setUser(await api<User>('/auth/profile/')); setError(''); }
    async function logout() { const token = getRefresh(); try {
        if (token)
            await post('/auth/logout/', { refresh: token });
    }
    finally {
        clearTokens();
        setUser(null);
        setError('');
    } }
    return <Context.Provider value={{ user, loading, error, login, logout, retry: () => setAttempt(v => v + 1) }}>{children}</Context.Provider>;
}
export function useAuth() { const ctx = useContext(Context); if (!ctx)
    throw new Error('Auth provider missing'); return ctx; }
