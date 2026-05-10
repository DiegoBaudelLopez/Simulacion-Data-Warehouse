import { Bar, Doughnut, Line } from 'react-chartjs-2'
import { StatCard, Loading, PALETTE, defaultScales, defaultLegend } from '../chartSetup'

export default function OrdenesView({ data }) {
  if (!data) return <Loading />

  const statusColors = { delivered: 'rgba(52,211,153,0.8)', shipped: 'rgba(59,130,246,0.8)', canceled: 'rgba(251,113,133,0.8)', invoiced: 'rgba(251,191,36,0.8)', processing: 'rgba(168,85,247,0.8)', created: 'rgba(34,211,238,0.8)', approved: 'rgba(96,165,250,0.8)', unavailable: 'rgba(100,116,139,0.8)' }

  const statusData = {
    labels: Object.keys(data.estados),
    datasets: [{ label: 'Ordenes', data: Object.values(data.estados), backgroundColor: Object.keys(data.estados).map(s => statusColors[s] || 'rgba(148,163,184,0.5)'), borderRadius: 6 }],
  }

  const meses = Object.keys(data.ordenes_por_mes)
  const mesData = {
    labels: meses.map(m => m.slice(2)),
    datasets: [{ label: 'Ordenes', data: Object.values(data.ordenes_por_mes), borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.15)', fill: true, tension: 0.4, pointRadius: 2 }],
  }

  const entregaData = {
    labels: Object.keys(data.histograma_entrega),
    datasets: [{ label: 'Ordenes', data: Object.values(data.histograma_entrega), backgroundColor: PALETTE.slice(0, 7), borderRadius: 6 }],
  }

  const puntualData = {
    labels: ['A tiempo', 'Tarde'],
    datasets: [{ data: [data.entregas_a_tiempo, data.entregas_tarde], backgroundColor: ['rgba(52,211,153,0.8)', 'rgba(251,113,133,0.8)'], borderWidth: 0, hoverOffset: 8 }],
  }

  const barOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } }, y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } } } }

  return (
    <>
      <div className="stats-grid">
        <StatCard icon="📦" value={data.total_ordenes} label="Total ordenes" color="blue" delay={1} />
        <StatCard icon="✅" value={data.entregas_a_tiempo} label="A tiempo" color="emerald" delay={2} />
        <StatCard icon="⏰" value={data.entregas_tarde} label="Tarde" color="amber" delay={3} />
        <StatCard icon="🚚" value={`${data.promedio_entrega_dias} dias`} label="Promedio entrega" color="cyan" delay={4} />
      </div>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">📊</span>Ordenes por Estado</div>
          <div className="chart-wrapper"><Bar data={statusData} options={barOpts} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">⏱️</span>Puntualidad de Entrega</div>
          <div className="chart-wrapper"><Doughnut data={puntualData} options={{ responsive: true, maintainAspectRatio: false, cutout: '60%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 20 } } } }} /></div>
        </div>
      </div>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">📅</span>Ordenes por Mes</div>
          <div className="chart-wrapper"><Line data={mesData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: defaultScales }} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">📦</span>Tiempo de Entrega (dias)</div>
          <div className="chart-wrapper"><Bar data={entregaData} options={barOpts} /></div>
        </div>
      </div>
    </>
  )
}
