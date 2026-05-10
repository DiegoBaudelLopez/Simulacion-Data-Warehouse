import { Bar, Doughnut } from 'react-chartjs-2'
import { StatCard, Loading, PALETTE, defaultScales } from '../chartSetup'

export default function ProductosView({ data }) {
  if (!data) return <Loading />

  const catLabels = Object.keys(data.top_categorias)
  const catData = {
    labels: catLabels,
    datasets: [{ label: 'Productos', data: Object.values(data.top_categorias), backgroundColor: PALETTE.slice(0, catLabels.length), borderRadius: 6 }],
  }

  const pesoData = {
    labels: Object.keys(data.rangos_peso),
    datasets: [{ data: Object.values(data.rangos_peso), backgroundColor: PALETTE.slice(0, 6), borderWidth: 0, hoverOffset: 8 }],
  }

  const fotoLabels = Object.keys(data.distribucion_fotos).slice(0, 10)
  const fotoData = {
    labels: fotoLabels.map(k => `${k} foto${k === '1' ? '' : 's'}`),
    datasets: [{ label: 'Productos', data: fotoLabels.map(k => data.distribucion_fotos[k]), backgroundColor: 'rgba(168,85,247,0.7)', borderRadius: 6 }],
  }

  const barOpts = { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } }, y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } } } }
  const vertBarOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } }, y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } } } }

  return (
    <>
      <div className="stats-grid">
        <StatCard icon="🏷️" value={data.total_productos} label="Total productos" color="blue" delay={1} />
        <StatCard icon="📂" value={data.total_categorias} label="Categorias" color="purple" delay={2} />
        <StatCard icon="⚖️" value={`${data.peso_promedio_g}g`} label="Peso promedio" color="emerald" delay={3} />
        <StatCard icon="📷" value={data.promedio_fotos} label="Fotos promedio" color="amber" delay={4} />
      </div>
      <div className="chart-section">
        <div className="chart-card chart-card--full">
          <div className="chart-card__title"><span className="chart-card__title-icon">📂</span>Top 15 Categorias de Productos</div>
          <div className="chart-wrapper" style={{ height: '400px' }}><Bar data={catData} options={barOpts} /></div>
        </div>
      </div>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">⚖️</span>Distribucion de Peso</div>
          <div className="chart-wrapper"><Doughnut data={pesoData} options={{ responsive: true, maintainAspectRatio: false, cutout: '55%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 16 } } } }} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">📷</span>Fotos por Producto</div>
          <div className="chart-wrapper"><Bar data={fotoData} options={vertBarOpts} /></div>
        </div>
      </div>
    </>
  )
}
