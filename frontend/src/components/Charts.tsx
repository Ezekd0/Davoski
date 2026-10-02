import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, ArcElement, BarElement, Tooltip, Legend, Filler } from 'chart.js';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import type { DashboardData } from '../types';
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, BarElement, Tooltip, Legend, Filler);
ChartJS.defaults.animation = false;
ChartJS.defaults.color = '#8091a9';
ChartJS.defaults.font.family = 'Inter, system-ui, sans-serif';
ChartJS.defaults.font.size = 11;
const palette = ['#f4667d', '#f6a558', '#8b7bf7', '#38bdf8', '#44d6b0', '#e5c46d', '#66758b'];
export function ActivityChart({ data }: {
    data: DashboardData;
}) { return <div className="chart activity-chart"><Line data={{ labels: data.timeline.map(t => new Date(t.date + 'T00:00:00').toLocaleDateString(undefined, { weekday: 'short', day: 'numeric' })), datasets: [{ label: 'Analyzed flows', data: data.timeline.map(t => t.count), borderColor: '#48c9ed', backgroundColor: 'rgba(56,189,248,.10)', fill: true, tension: .35, pointRadius: 3, pointBackgroundColor: '#48c9ed', borderWidth: 2 }] }} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false }, border: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#1a2534' }, border: { display: false } } } }}/></div>; }
export function CategoryChart({ data }: {
    data: DashboardData;
}) { return <div className="category-wrap"><div className="chart donut"><Doughnut data={{ labels: data.categories.map(t => t.threat_type), datasets: [{ data: data.categories.map(t => t.count), backgroundColor: palette, borderColor: '#111925', borderWidth: 4, hoverOffset: 5 }] }} options={{ responsive: true, maintainAspectRatio: false, cutout: '76%', plugins: { legend: { display: false } } }}/><div className="donut-label"><strong>{data.total_analyses}</strong><span>ANALYSES</span></div></div><div className="chart-legend">{data.categories.map((c, i) => <div key={c.threat_type}><span style={{ background: palette[i % palette.length] }}/><span>{c.threat_type}</span><strong>{c.count}</strong></div>)}</div></div>; }
export function SeverityChart({ data }: {
    data: DashboardData;
}) { const labels = ['Critical', 'High', 'Medium', 'Low']; return <div className="chart"><Bar data={{ labels, datasets: [{ label: 'Analyzed flows', data: labels.map(s => data.severities.find(v => v.severity === s)?.count || 0), backgroundColor: ['#f4667d', '#f6a558', '#e5c46d', '#44d6b0'], borderRadius: 5, maxBarThickness: 48 }] }} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false }, border: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#1a2534' }, border: { display: false } } } }}/></div>; }
