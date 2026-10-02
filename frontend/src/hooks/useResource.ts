import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
export function useResource<T>(path: string, pollMs = 0) {
    const [data, setData] = useState<T | null>(null), [error, setError] = useState(''), [loading, setLoading] = useState(true);
    const reload = useCallback(async () => { try {
        const result = await api<T>(path);
        setData(result);
        setError('');
    }
    catch (e) {
        setError(e instanceof Error ? e.message : 'Unable to load data');
    }
    finally {
        setLoading(false);
    } }, [path]);
    useEffect(() => { setLoading(true); void reload(); if (pollMs) {
        const timer = setInterval(() => void reload(), pollMs);
        return () => clearInterval(timer);
    } }, [reload, pollMs]);
    return { data, error, loading, reload };
}
