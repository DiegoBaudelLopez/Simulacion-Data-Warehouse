import { Bar, Doughnut, Line } from 'react-chartjs-2'
import { StatCard, Loading, defaultScales, defaultLegend } from '../chartSetup'

export default function ResumenView({ data }) {
  if (!data) return <Loading />

  const origenData = {
    labels: Object.keys(data.por_origen),
    datasets: [{ data: Object.values(data.por_origen), backgroundColor: ['rgba(59,130,246,0.8)', 'rgba(168,85,247,0.8)'], borderColor: ['#3b82f6', '#a855f7'], borderWidth: 2, hoverOffset: 8 }],
  }

  const tg = {}
  ;(data.timeline || []).forEach(t => {
    const k = t.timestamp?.slice(11, 16) || 'N/A'
    if (!tg[k]) tg[k] = { TCP: 0, UDP: 0 }
    tg[k][t.origen] = t.cantidad
  })
  const tLabels = Object.keys(tg)

  const timeData = {
    labels: tLabels,
    datasets: [
      { label: 'TCP', data: tLabels.map(k => tg[k].TCP), borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', fill: true, tension: 0.4, pointRadius: 2 },
      { label: 'UDP', data: tLabels.map(k => tg[k].UDP), borderColor: '#a855f7', backgroundColor: 'rgba(168,85,247,0.1)', fill: true, tension: 0.4, pointRadius: 2 },
    ],
  }

  return (
    <>
      <div className="stats-grid">
        <StatCard icon="📊" value={data.total} label="Total registros" color="blue" delay={1} />
        <StatCard icon="🔗" value={data.por_origen?.TCP || 0} label="Registros TCP" color="cyan" delay={2} />
        <StatCard icon="📡" value={data.por_origen?.UDP || 0} label="Registros UDP" color="emerald" delay={3} />
        <StatCard icon="🕐" value={data.fecha_inicio ? new Date(data.fecha_inicio).toLocaleTimeString() : '-'} label="Primera insercion" color="amber" delay={4} />
      </div>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">🍩</span>Distribucion por Origen</div>
          <div className="chart-wrapper"><Doughnut data={origenData} options={{ responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 20 } } } }} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">📈</span>Timeline de Ingesta</div>
          <div className="chart-wrapper"><Line data={timeData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: defaultLegend }, scales: defaultScales }} /></div>
        </div>
      </div>
    </>
  )
}
