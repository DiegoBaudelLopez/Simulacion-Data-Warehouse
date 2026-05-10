import { Bar } from 'react-chartjs-2'
import { StatCard, Loading, PALETTE } from '../chartSetup'

export default function GeoView({ data }) {
  if (!data) return <Loading />

  const estLabels = Object.keys(data.top_estados)
  const estData = {
    labels: estLabels,
    datasets: [{ label: 'Registros', data: Object.values(data.top_estados), backgroundColor: PALETTE.slice(0, estLabels.length), borderRadius: 6 }],
  }

  const cityLabels = Object.keys(data.top_ciudades).slice(0, 15)
  const cityData = {
    labels: cityLabels,
    datasets: [{ label: 'Registros', data: cityLabels.map(c => data.top_ciudades[c]), backgroundColor: 'rgba(34,211,238,0.7)', borderRadius: 6 }],
  }

  const barOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } }, y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } } } }
  const hBarOpts = { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,0.06)' } }, y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } } } }

  // Top 10 estados para tabla con coordenadas
  const topEstados = (data.estados_mapa || []).slice(0, 10)

  return (
    <>
      <div className="stats-grid">
        <StatCard icon="🌎" value={data.total_registros?.toLocaleString()} label="Registros geo" color="blue" delay={1} />
        <StatCard icon="🏛️" value={data.total_estados} label="Estados" color="cyan" delay={2} />
        <StatCard icon="🏙️" value={data.total_ciudades?.toLocaleString()} label="Ciudades" color="emerald" delay={3} />
        <StatCard icon="📍" value={topEstados[0]?.state || '-'} label="Estado principal" color="amber" delay={4} />
      </div>
      <div className="chart-section">
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">🗺️</span>Distribucion por Estado</div>
          <div className="chart-wrapper"><Bar data={estData} options={barOpts} /></div>
        </div>
        <div className="chart-card">
          <div className="chart-card__title"><span className="chart-card__title-icon">🏙️</span>Top 15 Ciudades</div>
          <div className="chart-wrapper" style={{ height: '380px' }}><Bar data={cityData} options={hBarOpts} /></div>
        </div>
      </div>

      <div className="table-section fade-in">
        <div className="table-header">
          <div className="table-header__title">📍 Coordenadas Promedio por Estado <span className="table-header__count">{topEstados.length}</span></div>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead><tr><th>Estado</th><th>Latitud</th><th>Longitud</th><th>Registros</th></tr></thead>
            <tbody>
              {topEstados.map((e, i) => (
                <tr key={i}>
                  <td><span className="badge badge--tcp">{e.state}</span></td>
                  <td>{e.lat}</td>
                  <td>{e.lng}</td>
                  <td>{e.count.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
