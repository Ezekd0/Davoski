import { AlertTriangle, ArrowUpRight, RefreshCw, Shield, Search, X } from 'lucide-react';
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import type { Threat, Severity } from '../types';
export const idLabel = (kind: string, id: number) => `${kind}-${String(id).padStart(4, '0')}`;
export const formatTime = (date: string) => new Date(date).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
export function Badge({ children, tone }: {
    children: ReactNode;
    tone?: string;
}) { return <span className={`badge tone-${(tone || String(children)).toLowerCase().replaceAll(' ', '-')}`}>{children}</span>; }
export function SeverityBadge({ severity }: {
    severity: Severity;
}) { return <Badge tone={severity}><span className="dot"/>{severity}</Badge>; }
export function PageHeading({ eyebrow, title, description, actions }: {
    eyebrow: string;
    title: string;
    description: string;
    actions?: ReactNode;
}) { return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div><div className="heading-actions">{actions}</div></div>; }
export function Panel({ title, subtitle, action, children, className = '' }: {
    title?: string;
    subtitle?: string;
    action?: ReactNode;
    children: ReactNode;
    className?: string;
}) { return <section className={`panel ${className}`}>{title && <div className="panel-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{action}</div>}{children}</section>; }
export function Empty({ title = 'No records yet', message = 'Analyze a traffic sample to start building your security history.' }: {
    title?: string;
    message?: string;
}) { return <div className="empty"><Shield size={32}/><h3>{title}</h3><p>{message}</p></div>; }
export function Loading() { return <div className="loading"><RefreshCw className="spin" size={20}/> Loading security data…</div>; }
export function ErrorState({ error, retry }: {
    error: string;
    retry?: () => void;
}) { return <div className="error-state" role="alert"><AlertTriangle size={18}/><span>{error}</span>{retry && <button className="btn small" onClick={retry}><RefreshCw size={14}/>Retry</button>}</div>; }
export function DemoNotice() { return <div className="demo-notice"><Shield size={15}/><span><strong>Academic demo environment.</strong> Rule-based analysis, illustrative scores, and simulated responses. No trained model or live network monitoring.</span><Badge tone="medium">DEMO</Badge></div>; }
export function ThreatTable({ threats }: {
    threats: Threat[];
}) { if (!threats.length)
    return <Empty />; return <div className="table-scroll"><table><thead><tr><th>Threat / ID</th><th>Source → Destination</th><th>Severity</th><th>Demo score</th><th>Status</th><th>Detected</th><th /></tr></thead><tbody>{threats.map(t => <tr key={t.id}><td><Link className="threat-link" to={`/threats/${t.id}`}>{t.threat_type}</Link><div className="muted mono tiny">{idLabel('THR', t.id)}</div></td><td><div className="mono">{t.source_ip}</div><div className="muted mono tiny">→ {t.destination_ip}</div></td><td><SeverityBadge severity={t.severity}/></td><td><div className="score-cell"><span>{t.confidence}%</span><span className="mini-track"><i style={{ width: `${t.confidence}%` }}/></span></div></td><td><Badge>{t.status}</Badge></td><td className="muted nowrap">{formatTime(t.created_at)}</td><td><Link className="icon-button" to={`/threats/${t.id}`} aria-label={`View threat ${t.id}`}><ArrowUpRight size={17}/></Link></td></tr>)}</tbody></table></div>; }
export function SearchInput({ value, onChange, placeholder = 'Search records…' }: {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
}) { return <label className="search-input"><Search size={16}/><input aria-label={placeholder} placeholder={placeholder} value={value} onChange={e => onChange(e.target.value)}/>{value && <button aria-label="Clear search" onClick={() => onChange('')}><X size={14}/></button>}</label>; }
