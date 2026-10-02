import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, Plus, ShieldAlert } from 'lucide-react';
import { useResource } from '../hooks/useResource';
import { post } from '../services/api';
import type { Threat, Incident, AuditEvent } from '../types';
import { PageHeading, Panel, Loading, ErrorState, ThreatTable, SearchInput, Badge, idLabel, formatTime, Empty } from '../components/UI';
import ThreatResult from '../components/ThreatResult';
export function Threats() { const { data, loading, error, reload } = useResource<Threat[]>('/threats/'); const [search, setSearch] = useState(''), [severity, setSeverity] = useState(''), [status, setStatus] = useState(''), [type, setType] = useState(''); const filtered = data?.filter(t => (!severity || t.severity === severity) && (!status || t.status === status) && (!type || t.threat_type === type) && [t.source_ip, t.destination_ip, t.threat_type, idLabel('THR', t.id)].join(' ').toLowerCase().includes(search.toLowerCase())) || []; return <><PageHeading eyebrow="THREAT INTELLIGENCE" title="Threat history" description="Investigate detections, inspect flow details, and track response status." actions={<Link className="btn primary" to="/analysis"><Plus size={16}/>New analysis</Link>}/>{error && <ErrorState error={error} retry={reload}/>}<Panel><div className="filters"><SearchInput value={search} onChange={setSearch} placeholder="Search IP, type or threat ID…"/><select aria-label="Severity filter" value={severity} onChange={e => setSeverity(e.target.value)}><option value="">All severities</option>{['Critical', 'High', 'Medium', 'Low'].map(s => <option key={s}>{s}</option>)}</select><select aria-label="Status filter" value={status} onChange={e => setStatus(e.target.value)}><option value="">All statuses</option>{['Detected', 'Safe', 'Acknowledged', 'Investigating', 'Contained', 'Resolved'].map(s => <option key={s}>{s}</option>)}</select><select aria-label="Threat type filter" value={type} onChange={e => setType(e.target.value)}><option value="">All threat types</option>{['DDoS', 'PortScan', 'Botnet', 'Infiltration', 'Web Attack', 'Brute Force', 'Benign'].map(s => <option key={s}>{s}</option>)}</select></div>{loading ? <Loading /> : <ThreatTable threats={filtered}/>}<div className="table-footer"><span>{filtered.length} of {data?.length || 0} records</span><span>Persistent API history</span></div></Panel></>; }
export function ThreatDetail() { const { id } = useParams(); const { data: threat, loading, error, reload } = useResource<Threat>(`/threats/${id}/`); const audit = useResource<AuditEvent[]>('/audit/'); const [action, setAction] = useState('Investigate'), [busy, setBusy] = useState(false), [message, setMessage] = useState(''), [actionError, setActionError] = useState(''); async function respond() { setBusy(true); setActionError(''); setMessage(''); try {
    await post(`/threats/${id}/respond/`, { action });
    setMessage(`${action} recorded as a simulated response. No host or network changes executed.`);
    await reload();
    await audit.reload();
}
catch (e) {
    setActionError(e instanceof Error ? e.message : 'Response failed');
}
finally {
    setBusy(false);
} } async function createIncident() { if (!threat)
    return; setBusy(true); setActionError(''); try {
    const inc = await post<Incident>('/incidents/', { title: `${threat.threat_type} · ${threat.source_ip}`, threat_ids: [threat.id] });
    setMessage(`Incident ${idLabel('INC', inc.id)} created.`);
    await reload();
    await audit.reload();
}
catch (e) {
    setActionError(e instanceof Error ? e.message : 'Incident creation failed');
}
finally {
    setBusy(false);
} } return <><Link className="back-link" to="/threats"><ArrowLeft size={15}/>Back to threats</Link><PageHeading eyebrow="DETECTION DETAILS" title={threat ? `${idLabel('THR', threat.id)} · ${threat.threat_type}` : 'Threat details'} description="Review the evidence and record a safe response."/>{error && <ErrorState error={error} retry={reload}/>} {loading ? <Loading /> : threat && <div className="detail-layout"><ThreatResult threat={threat}/><div><Panel title="Response console" subtitle="All response actions are simulated"><div className="form-panel"><div className="status-row"><span>Current status</span><Badge>{threat.status}</Badge></div><p className="muted">{threat.response_status}</p><label>Response action<select value={action} onChange={e => setAction(e.target.value)}>{['Investigate', 'Acknowledge', 'Contain', 'Block source', 'Isolate', 'Resolve'].map(s => <option key={s}>{s}</option>)}</select></label><button className="btn primary full" disabled={busy} onClick={() => void respond()}><ShieldAlert size={16}/>{busy ? 'Saving…' : 'Record simulated response'}</button><button className="btn full" disabled={busy} onClick={() => void createIncident()}><Plus size={16}/>Create related incident</button>{actionError && <ErrorState error={actionError}/>} {message && <div role="status" className="success-state">{message}</div>}{threat.incident_ids.length > 0 && <div className="linked-records"><h3>Related incidents</h3>{threat.incident_ids.map(inc => <Link key={inc} to={`/incidents/${inc}`}>{idLabel('INC', inc)} →</Link>)}</div>}</div></Panel><Panel title="Network features" subtitle="Submitted flow values"><div className="key-value-list">{Object.entries(threat.features).map(([key, value]) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong className="mono">{String(value)}</strong></div>)}</div></Panel><Panel title="Threat timeline"><div className="timeline">{audit.loading ? <Loading /> : audit.error ? <ErrorState error={audit.error} retry={audit.reload}/> : audit.data?.filter(a => a.threat === threat.id).map(a => <div key={a.id}><span className="timeline-dot"/><p>{a.action}<small>{formatTime(a.created_at)} · {a.actor_name}</small></p></div>)}</div></Panel></div></div>}</>; }
