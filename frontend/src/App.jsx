import { useState, useEffect, useCallback } from 'react'
import './index.css'
import ResumenView from './views/ResumenView'
import OrdenesView from './views/OrdenesView'
import ProductosView from './views/ProductosView'
import ItemsView from './views/ItemsView'
import GeoView from './views/GeoView'
import SensoresView from './views/SensoresView'
import DatosView from './views/DatosView'

const API_BASE = 'http://127.0.0.1:5000'

const TABS = [
  { id: 'resumen',   label: 'Resumen',       icon: '📊' },
  { id: 'ordenes',   label: 'Ordenes',       icon: '📦' },
  { id: 'productos', label: 'Productos',     icon: '🏷️' },
  { id: 'items',     label: 'Precios/Envio', icon: '💰' },
  { id: 'geo',       label: 'Geo',           icon: '🌎' },
  { id: 'sensores',  label: 'Sensores',      icon: '🌡️' },
  { id: 'datos',     label: 'Datos',         icon: '🗄️' },
]

const ENDPOINTS = {
  resumen:   '/api/datos/resumen',
  sensores:  '/api/datos/sensores',
  datos:     '/api/datos?limite=200',
  ordenes:   '/api/analytics/ordenes',
  productos: '/api/analytics/productos',
  items:     '/api/analytics/items',
  geo:       '/api/analytics/geo',
}

function App() {
  const [tab, setTab] = useState('resumen')
  const [data, setData] = useState({})
  const [error, setError] = useState(null)
  const [loadingTab, setLoadingTab] = useState(null)

  const loadTab = useCallback(async (tabId) => {
    if (data[tabId]) return  // Already loaded
    setLoadingTab(tabId)
    try {
      const url = ENDPOINTS[tabId]
      if (!url) return
      const res = await fetch(`${API_BASE}${url}`)
      const json = await res.json()
      setData(prev => ({ ...prev, [tabId]: json }))
    } catch (err) {
      setError('No se pudo conectar con la API. Asegurate de que este corriendo en el puerto 5000.')
      console.error(err)
    } finally {
      setLoadingTab(null)
    }
  }, [data])

  useEffect(() => { loadTab(tab) }, [tab])  // eslint-disable-line react-hooks/exhaustive-deps

  if (error) {
    return (
      <div className="app">
        <div className="header"><h1 className="header__title">Data Warehouse Dashboard</h1></div>
        <div className="empty-state">
          <div className="empty-state__icon">⚠️</div>
          <div className="empty-state__text">{error}</div>
        </div>
      </div>
    )
  }

  const isLoading = loadingTab === tab && !data[tab]

  return (
    <div className="app">
      <header className="header">
        <h1 className="header__title">Data Warehouse Dashboard</h1>
        <p className="header__subtitle">Simulacion de Data Warehouse - Fase 3: Visualizacion</p>
        <div className="header__status">
          <span className="header__status-dot" />
          Supabase conectado
        </div>
      </header>

      <nav className="tabs">
        {TABS.map(t => (
          <button key={t.id} className={`tabs__btn ${tab === t.id ? 'tabs__btn--active' : ''}`} onClick={() => setTab(t.id)}>
            <span className="tabs__icon">{t.icon}</span>{t.label}
          </button>
        ))}
      </nav>

      {isLoading
        ? <div className="loading"><div className="loading__spinner" /><span className="loading__text">Cargando datos...</span></div>
        : <>
            {tab === 'resumen'   && <ResumenView data={data.resumen} />}
            {tab === 'ordenes'   && <OrdenesView data={data.ordenes} />}
            {tab === 'productos' && <ProductosView data={data.productos} />}
            {tab === 'items'     && <ItemsView data={data.items} />}
            {tab === 'geo'       && <GeoView data={data.geo} />}
            {tab === 'sensores'  && <SensoresView data={data.sensores} />}
            {tab === 'datos'     && <DatosView data={data.datos} />}
          </>
      }
    </div>
  )
}

export default App
