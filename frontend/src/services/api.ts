const BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');
let accessToken: string | null = null;
let refreshToken: string | null = sessionStorage.getItem('ctdrs.refresh');
let refreshing: Promise<boolean> | null = null;
export function setTokens(access: string, refresh: string) { accessToken = access; refreshToken = refresh; sessionStorage.setItem('ctdrs.refresh', refresh); }
export function clearTokens() { accessToken = null; refreshToken = null; sessionStorage.removeItem('ctdrs.refresh'); }
export function getRefresh() { return refreshToken; }
export class ApiError extends Error {
    constructor(public status: number, message: string) { super(message); }
}
function describeError(value: unknown): string {
    if (typeof value === 'string')
        return value;
    if (Array.isArray(value))
        return value.map(describeError).join(' ');
    if (value && typeof value === 'object')
        return Object.entries(value).filter(([key]) => key !== 'status').map(([key, v]) => key === 'error' || key === 'detail' ? describeError(v) : `${key.replaceAll('_', ' ')}: ${describeError(v)}`).join(' · ');
    return 'Request failed. Please try again.';
}
async function refresh(): Promise<boolean> {
    if (!refreshToken)
        return false;
    try {
        const r = await fetch(`${BASE}/auth/refresh/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh: refreshToken }), signal: AbortSignal.timeout(10000) });
        if (!r.ok) {
            clearTokens();
            return false;
        }
        const data = await r.json();
        setTokens(data.access, data.refresh || refreshToken);
        return true;
    }
    catch {
        throw new ApiError(0, 'API unavailable. Check the backend connection and retry.');
    }
}
export async function api<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
    let response: Response;
    try {
        response = await fetch(`${BASE}${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}), ...options.headers }, signal: AbortSignal.timeout(15000) });
    }
    catch {
        throw new ApiError(0, 'API unavailable. Check the backend connection and retry.');
    }
    if (response.status === 401 && retry && !path.startsWith('/auth/login/')) {
        refreshing ??= refresh().finally(() => { refreshing = null; });
        if (await refreshing)
            return api<T>(path, options, false);
        clearTokens();
        window.dispatchEvent(new Event('auth-expired'));
        throw new ApiError(401, 'Your session expired. Please sign in again.');
    }
    if (!response.ok) {
        const data = await response.json().catch(() => ({ detail: 'The server could not complete the request.' }));
        throw new ApiError(response.status, describeError(data));
    }
    return response.status === 204 ? undefined as T : response.json();
}
export const post = <T>(path: string, data: unknown) => api<T>(path, { method: 'POST', body: JSON.stringify(data) });
export const patch = <T>(path: string, data: unknown) => api<T>(path, { method: 'PATCH', body: JSON.stringify(data) });
