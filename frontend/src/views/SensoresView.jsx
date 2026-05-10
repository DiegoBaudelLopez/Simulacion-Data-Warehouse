import { Bar, Line } from 'react-chartjs-2'
import { Loading, defaultScales, defaultLegend } from '../chartSetup'

export default function SensoresView({ data }) {
  if (!data) return <Loading />
  const sensores = data.sensores || []
  if (sensores.length === 0) return <div className="empty-state"><div className="empty-state__icon">📡</div><div className="empty-state__text">No hay lecturas de sensores</div></div>

  const porTipo = {}
  sensores.forEach(s => { if (!porTipo[s.type]) porTipo[s.type] = []; porTipo[s.type].push(s) })
  const tipos = Object.keys(porTipo)
  const colors = { temperatura: '#fb7185', humedad: '#3b82f6', velocidad: '#34d399', presion: '#fbbf24' }

  const promedios = tipos.map(t => { const v = porTipo[t].map(s => s.value); return Math.round(v.reduce((a, b) => a + b, 0) / v.length * 100) / 100 })
  const avgData = { labels: tipos.map(t => t.charAt(0).toUpperCase() + t.slice(1)), datasets: [{ label: 'Promedio', data: promedios, backgroundColor: tipos.map(t => colors[t] || '#94a3b8'), borderRadius: 6 }] }

  const timeDs = tipos.map(t => ({ label: t.charAt(0).toUpperCase() + t.slice(1), data: porTipo[t].map(s => s.value), borderColor: colors[t] || '#94a3b8', backgroundColor: 'transparent', tension: 0.3, pointRadius: 2 }))
  const timeData = { labels: sensores.map((_, i) => i + 1), datasets: timeDs }

  const ultimas = sensores.slice(-12).reverse()

  return (
    <>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">📊</span>Promedio por Tipo</div>
          <div className="chart-wrapper"><Bar data={avgData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#94a3b8' }, grid: { display: false } }, y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } } } }} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">🌡️</span>Lecturas en el Tiempo</div>
          <div className="chart-wrapper"><Line data={timeData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: defaultLegend }, scales: defaultScales }} /></div>
        </div>
      </div>
      <div className="sensors-grid">
        {ultimas.map((s, i) => (
          <div className="sensor-card fade-in" key={i} style={{ animationDelay: `${i * 0.03}s` }}>
            <div className="sensor-card__header"><span className="sensor-card__id">{s.sensor_id}</span><span className="sensor-card__type">{s.type}</span></div>
            <div className="sensor-card__value">{s.value}<span className="sensor-card__unit">{s.unit}</span></div>
            <div className="sensor-card__time">{s.timestamp ? new Date(s.timestamp).toLocaleString() : '-'}</div>
          </div>
        ))}
      </div>
    </>
  )
}
