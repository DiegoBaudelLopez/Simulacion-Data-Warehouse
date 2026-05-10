import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler,
  ScatterController,
} from 'chart.js'

ChartJS.register(
  CategoryScale, LinearScale, BarElement, PointElement,
  LineElement, ArcElement, Title, Tooltip, Legend, Filler,
  ScatterController
)

export const CHART_COLORS = {
  blue: 'rgba(59, 130, 246, 0.8)',
  purple: 'rgba(168, 85, 247, 0.8)',
  cyan: 'rgba(34, 211, 238, 0.8)',
  emerald: 'rgba(52, 211, 153, 0.8)',
  amber: 'rgba(251, 191, 36, 0.8)',
  rose: 'rgba(251, 113, 133, 0.8)',
  slate: 'rgba(148, 163, 184, 0.5)',
}

export const PALETTE = [
  CHART_COLORS.blue, CHART_COLORS.purple, CHART_COLORS.cyan,
  CHART_COLORS.emerald, CHART_COLORS.amber, CHART_COLORS.rose,
  'rgba(96,165,250,0.8)', 'rgba(192,132,252,0.8)', 'rgba(45,212,191,0.8)',
  'rgba(74,222,128,0.8)', 'rgba(253,186,116,0.8)', 'rgba(244,114,182,0.8)',
  'rgba(129,140,248,0.8)', 'rgba(34,197,94,0.8)', 'rgba(249,115,22,0.8)',
]

export const defaultScales = {
  x: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: 'rgba(148,163,184,0.06)' } },
  y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } },
}

export const defaultLegend = { labels: { color: '#94a3b8', font: { family: 'Inter' } } }

export function StatCard({ icon, value, label, color, delay = 1 }) {
  return (
    <div className={`stat-card stat-card--${color} fade-in fade-in-delay-${delay}`}>
      <div className="stat-card__icon">{icon}</div>
      <div className="stat-card__value">{typeof value === 'number' ? value.toLocaleString() : value}</div>
      <div className="stat-card__label">{label}</div>
    </div>
  )
}

export function Loading() {
  return <div className="loading"><div className="loading__spinner" /><span className="loading__text">Cargando...</span></div>
}

export function EmptyState({ icon = '📭', text = 'Sin datos' }) {
  return <div className="empty-state"><div className="empty-state__icon">{icon}</div><div className="empty-state__text">{text}</div></div>
}
