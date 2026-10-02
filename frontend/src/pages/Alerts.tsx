import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Check, RefreshCw } from 'lucide-react';
import { useResource } from '../hooks/useResource';
import { post } from '../services/api';
import type { Alert, Settings } from '../types';
import { PageHeading, Panel, Loading, ErrorState, SeverityBadge, Badge, Empty, formatTime, idLabel } from '../components/UI';
export default function Alerts() { const prefs = useResource<Settings>('/settings/'); const { data, loading, error, reload } = useResource<Alert[]>('/alerts/', (prefs.data?.polling_seconds || 30) * 1000); const [filter, setFilter] = useState('All'), [busy, setBusy] = useState<number | null>(null), [actionError, setActionError] = useState(''); async function acknowledge(id: number) { setBusy(id); setActionError(''); try {
    await post(`/alerts/${id}/acknowledge/`, {});
    await reload();
}
catch (e) {
    setActionError(e instanceof Error ? e.message : 'Unable to acknowledge');
}
finally {
    setBusy(null);
} } const filtered = data?.filter(a => filter === 'All' || a.status === filter) || []; return <><PageHeading eyebrow="EVENT MONITORING" title="Alert center" description={`Workspace events refresh every ${prefs.data?.polling_seconds || 30} seconds. Acknowledge alerts after review.`} actions={<button className="btn" onClick={() => void reload()}><RefreshCw size={15}/>Refresh alerts</button>}/>{(error || actionError) && <ErrorState error={error || actionError} retry={reload}/>}<Panel><div className="tabs">{['All', 'Unread', 'Acknowledged'].map(s => <button key={s} className={filter === s ? 'active' : ''} onClick={() => setFilter(s)}>{s}<span>{data?.filter(a => s === 'All' || a.status === s).length || 0}</span></button>)}</div>{loading ? <Loading /> : !filtered.length ? <Empty title="You're all caught up" message="No alerts match this view. New analysis and response events appear here."/> : <div className="alert-list">{filtered.map(a => <div className={`alert-row ${a.status === 'Unread' ? 'unread' : ''}`} key={a.id}><span className={`alert-symbol ${a.severity.toLowerCase()}`}><Bell size={19}/></span><div className="alert-content"><div><SeverityBadge severity={a.severity}/><span className="mono tiny muted">{idLabel('ALT', a.id)}</span></div><h3>{a.message}</h3><p>{formatTime(a.created_at)} {a.threat && <Link to={`/threats/${a.threat}`}>· View threat →</Link>} {a.incident && <Link to={`/incidents/${a.incident}`}>· View incident →</Link>}</p></div>{a.status === 'Unread' ? <button className="btn small" disabled={busy === a.id} onClick={() => void acknowledge(a.id)}><Check size={14}/>{busy === a.id ? 'Saving…' : 'Acknowledge'}</button> : <Badge>Acknowledged</Badge>}</div>)}</div>}</Panel></>; }
