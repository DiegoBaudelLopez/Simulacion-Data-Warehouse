import { Bar, Doughnut } from 'react-chartjs-2'
import { Scatter } from 'react-chartjs-2'
import { StatCard, Loading, PALETTE, defaultScales } from '../chartSetup'

export default function ItemsView({ data }) {
  if (!data) return <Loading />

  const precioData = {
    labels: Object.keys(data.rangos_precio),
    datasets: [{ label: 'Items', data: Object.values(data.rangos_precio), backgroundColor: PALETTE.slice(0, 6), borderRadius: 6 }],
  }

  const envioData = {
    labels: Object.keys(data.rangos_envio),
    datasets: [{ label: 'Items', data: Object.values(data.rangos_envio), backgroundColor: PALETTE.slice(6, 12), borderRadius: 6 }],
  }

  const ratioData = {
    labels: Object.keys(data.rangos_ratio_envio),
    datasets: [{ data: Object.values(data.rangos_ratio_envio), backgroundColor: PALETTE.slice(0, 6), borderWidth: 0, hoverOffset: 8 }],
  }

  const scatterData = {
    datasets: [{
      label: 'Precio vs Envio',
      data: (data.scatter_precio_envio || []).map(p => ({ x: p.precio, y: p.envio })),
      backgroundColor: 'rgba(59,130,246,0.5)',
      pointRadius: 4,
      pointHoverRadius: 6,
    }],
  }

  const barOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } }, y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } } } }
  const scatterOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { title: { display: true, text: 'Precio (R$)', color: '#94a3b8' }, ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } }, y: { title: { display: true, text: 'Envio (R$)', color: '#94a3b8' }, ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } } } }

  return (
    <>
      <div className="stats-grid">
        <StatCard icon="🛒" value={data.total_items} label="Total items" color="blue" delay={1} />
        <StatCard icon="💵" value={`R$${data.precio_promedio}`} label="Precio promedio" color="emerald" delay={2} />
        <StatCard icon="🚚" value={`R$${data.envio_promedio}`} label="Envio promedio" color="amber" delay={3} />
        <StatCard icon="💰" value={`R$${(data.ingreso_total / 1000000).toFixed(1)}M`} label="Ingreso total" color="cyan" delay={4} />
      </div>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">💵</span>Distribucion de Precios</div>
          <div className="chart-wrapper"><Bar data={precioData} options={barOpts} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">🚚</span>Costos de Envio</div>
          <div className="chart-wrapper"><Bar data={envioData} options={barOpts} /></div>
        </div>
      </div>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">📊</span>Ratio Envio/Precio</div>
          <div className="chart-wrapper"><Doughnut data={ratioData} options={{ responsive: true, maintainAspectRatio: false, cutout: '55%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 16 } } } }} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">🔵</span>Precio vs Costo de Envio</div>
          <div className="chart-wrapper"><Scatter data={scatterData} options={scatterOpts} /></div>
        </div>
      </div>
    </>
  )
}
