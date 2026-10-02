import { useState, type FormEvent } from 'react';
import { ShieldCheck, ArrowRight, Activity, LockKeyhole, ScanLine } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { post } from '../services/api';
import { ErrorState } from '../components/UI';
export default function Login() { const { login, error: sessionError, retry } = useAuth(); const [register, setRegister] = useState(false), [username, setUsername] = useState(''), [password, setPassword] = useState(''), [email, setEmail] = useState(''), [busy, setBusy] = useState(false), [error, setError] = useState(''), [notice, setNotice] = useState(''); async function submit(e: FormEvent) { e.preventDefault(); setBusy(true); setError(''); try {
    if (register) {
        await post('/auth/register/', { username, password, email });
        setRegister(false);
        setNotice('Account created. Sign in to your new analyst workspace.');
    }
    else
        await login(username, password);
}
catch (e) {
    setError(e instanceof Error ? e.message : 'Unable to sign in');
}
finally {
    setBusy(false);
} } return <div className="login-page"><div className="login-story"><div className="brand"><div className="brand-icon"><ShieldCheck size={30}/></div><div><strong>AI-CTDRS<span className="brand-period">.</span></strong><span>SECURITY OPERATIONS</span></div></div><div className="login-visual"><div className="radar"><div className="radar-line"/><ShieldCheck size={64}/><i /><i /><i /></div><span className="eyebrow">DETECT. UNDERSTAND. RESPOND.</span><h1>Your command center<br />for cyber defense.</h1><p>Turn network signals into actionable intelligence. Investigate threats, coordinate incidents, and see the story behind every detection.</p><div className="login-features"><span><Activity size={16}/>Threat intelligence</span><span><ScanLine size={16}/>Explainable analysis</span><span><LockKeyhole size={16}/>Incident response</span></div></div><p className="tiny muted">Academic demonstration · Analysis and responses are simulated</p></div><div className="login-form-side"><div className="login-form"><span className="eyebrow">SECURE WORKSPACE ACCESS</span><h2>{register ? 'Create your account' : 'Welcome back'}</h2><p>{register ? 'Set up your security analyst workspace.' : 'Sign in to your security operations workspace.'}</p>{(error || sessionError) && <ErrorState error={error || sessionError} retry={sessionError.includes('unavailable') ? retry : undefined}/>} {notice && <div className="success-state">{notice}</div>}<form onSubmit={submit}><label>Username<input required autoComplete="username" value={username} onChange={e => setUsername(e.target.value)} placeholder="Enter your username"/></label>{register && <label>Email<input required type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="analyst@example.com"/></label>}<label>Password<input required type="password" minLength={register ? 8 : 1} autoComplete={register ? 'new-password' : 'current-password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter your password"/></label><button className="btn primary" disabled={busy}>{busy ? 'Please wait…' : register ? 'Create analyst account' : 'Sign in to workspace'}<ArrowRight size={17}/></button></form><button className="text-button" onClick={() => { setRegister(!register); setError(''); setNotice(''); }}>{register ? 'Already have an account? Sign in' : 'New analyst? Create an account'}</button><div className="demo-credentials"><span className="badge tone-medium">LOCAL DEMO</span><p>After running the seed command:</p><div><code>admin</code><span>/</span><code>DemoSecure!2026</code></div><small>Use your configured DEMO_PASSWORD if overridden.</small></div></div></div></div>; }
