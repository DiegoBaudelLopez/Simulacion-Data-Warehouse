"""
API REST - Fase 3
Expone los datos almacenados en PostgreSQL (Supabase) y analisis
de los datasets CSV mediante endpoints HTTP.
Utiliza Flask para servir datos en formato JSON.
"""

import os
import sys
import csv
import json
import random
import time as _time
from collections import Counter, defaultdict
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

# Importar configuracion de BD desde el directorio server/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))
from db_config import get_connection

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Cache simple en memoria (evita re-leer CSVs grandes en cada request)
_cache = {}
_CACHE_TTL = 120  # segundos


# ---------------------------------------------------------------------------
# Helpers para leer CSVs
# ---------------------------------------------------------------------------

def read_csv(filename, limit=None):
    """Lee un CSV y retorna una lista de diccionarios (con cache)."""
    cache_key = f"{filename}_{limit}"
    now = _time.time()
    if cache_key in _cache and (now - _cache[cache_key]["ts"]) < _CACHE_TTL:
        return _cache[cache_key]["data"]

    filepath = os.path.join(DATA_DIR, filename)
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            rows.append(row)
    _cache[cache_key] = {"data": rows, "ts": now}
    return rows


# ---------------------------------------------------------------------------
# Endpoint principal: /api/datos (datos crudos del warehouse)
# ---------------------------------------------------------------------------

@app.route("/api/datos", methods=["GET"])
def obtener_datos():
    """
    Retorna los datos almacenados en datos_warehouse.
    Parametros opcionales:
      - origen: filtrar por 'TCP' o 'UDP'
      - limite: cantidad maxima de registros (default 500)
      - offset: paginacion
    """
    origen = request.args.get("origen")
    limite = request.args.get("limite", 500, type=int)
    offset = request.args.get("offset", 0, type=int)

    conn = get_connection()
    cur = conn.cursor()

    if origen:
        cur.execute(
            "SELECT id, origen, contenido, fecha FROM datos_warehouse "
            "WHERE origen = %s ORDER BY fecha DESC LIMIT %s OFFSET %s",
            (origen.upper(), limite, offset),
        )
    else:
        cur.execute(
            "SELECT id, origen, contenido, fecha FROM datos_warehouse "
            "ORDER BY fecha DESC LIMIT %s OFFSET %s",
            (limite, offset),
        )

    rows = cur.fetchall()
    datos = [
        {
            "id": r[0],
            "origen": r[1],
            "contenido": r[2],
            "fecha": r[3].isoformat() if r[3] else None,
        }
        for r in rows
    ]

    cur.close()
    conn.close()
    return jsonify({"total": len(datos), "datos": datos})


# ---------------------------------------------------------------------------
# Endpoint de resumen/estadisticas generales
# ---------------------------------------------------------------------------

@app.route("/api/datos/resumen", methods=["GET"])
def resumen():
    """Retorna estadisticas generales del warehouse."""
    conn = get_connection()
    cur = conn.cursor()

    # Total por origen
    cur.execute(
        "SELECT origen, COUNT(*) FROM datos_warehouse GROUP BY origen"
    )
    por_origen = {r[0]: r[1] for r in cur.fetchall()}

    # Total general
    cur.execute("SELECT COUNT(*) FROM datos_warehouse")
    total = cur.fetchone()[0]

    # Rango de fechas
    cur.execute(
        "SELECT MIN(fecha), MAX(fecha) FROM datos_warehouse"
    )
    fecha_min, fecha_max = cur.fetchone()

    # Ingesta por minuto (para grafica de timeline)
    cur.execute("""
        SELECT
            date_trunc('minute', fecha) AS minuto,
            origen,
            COUNT(*) AS cantidad
        FROM datos_warehouse
        GROUP BY minuto, origen
        ORDER BY minuto
    """)
    timeline = [
        {
            "timestamp": r[0].isoformat() if r[0] else None,
            "origen": r[1],
            "cantidad": r[2],
        }
        for r in cur.fetchall()
    ]

    cur.close()
    conn.close()

    return jsonify({
        "total": total,
        "por_origen": por_origen,
        "fecha_inicio": fecha_min.isoformat() if fecha_min else None,
        "fecha_fin": fecha_max.isoformat() if fecha_max else None,
        "timeline": timeline,
    })


# ---------------------------------------------------------------------------
# Endpoint: Sensores UDP
# ---------------------------------------------------------------------------

@app.route("/api/datos/sensores", methods=["GET"])
def obtener_sensores():
    """Parsea los registros UDP (JSON de sensores)."""
    limite = request.args.get("limite", 200, type=int)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT contenido, fecha FROM datos_warehouse "
        "WHERE origen = 'UDP' ORDER BY fecha LIMIT %s",
        (limite,),
    )

    sensores = []
    for row in cur.fetchall():
        try:
            data = json.loads(row[0])
            data["fecha_insercion"] = row[1].isoformat() if row[1] else None
            sensores.append(data)
        except json.JSONDecodeError:
            continue

    cur.close()
    conn.close()

    return jsonify({"total": len(sensores), "sensores": sensores})


# ---------------------------------------------------------------------------
# Endpoint: Analisis de Ordenes
# ---------------------------------------------------------------------------

@app.route("/api/analytics/ordenes", methods=["GET"])
def analytics_ordenes():
    """
    Analisis de ordenes: distribucion por estado, ordenes por mes,
    tiempos de entrega promedio, etc.
    """
    orders = read_csv("olist_orders_dataset.csv", limit=20000)

    # Distribucion por estado
    status_counts = Counter(o["order_status"] for o in orders)

    # Ordenes por mes (YYYY-MM)
    por_mes = Counter()
    for o in orders:
        ts = o.get("order_purchase_timestamp", "")
        if ts and len(ts) >= 7:
            por_mes[ts[:7]] += 1
    por_mes_sorted = dict(sorted(por_mes.items()))

    # Tiempos de entrega (dias entre compra y entrega al cliente)
    tiempos_entrega = []
    for o in orders:
        compra = o.get("order_purchase_timestamp", "")
        entrega = o.get("order_delivered_customer_date", "")
        if compra and entrega:
            try:
                dt_compra = datetime.strptime(compra[:19], "%Y-%m-%d %H:%M:%S")
                dt_entrega = datetime.strptime(entrega[:19], "%Y-%m-%d %H:%M:%S")
                dias = (dt_entrega - dt_compra).days
                if 0 <= dias <= 120:
                    tiempos_entrega.append(dias)
            except ValueError:
                pass

    # Histograma de tiempos de entrega (agrupado por rangos)
    rangos = {"0-5": 0, "6-10": 0, "11-15": 0, "16-20": 0, "21-30": 0, "31-60": 0, "60+": 0}
    for d in tiempos_entrega:
        if d <= 5: rangos["0-5"] += 1
        elif d <= 10: rangos["6-10"] += 1
        elif d <= 15: rangos["11-15"] += 1
        elif d <= 20: rangos["16-20"] += 1
        elif d <= 30: rangos["21-30"] += 1
        elif d <= 60: rangos["31-60"] += 1
        else: rangos["60+"] += 1

    # Porcentaje de entrega a tiempo vs tarde
    entregas_a_tiempo = 0
    entregas_tarde = 0
    for o in orders:
        entrega = o.get("order_delivered_customer_date", "")
        estimada = o.get("order_estimated_delivery_date", "")
        if entrega and estimada:
            try:
                dt_ent = datetime.strptime(entrega[:19], "%Y-%m-%d %H:%M:%S")
                dt_est = datetime.strptime(estimada[:19], "%Y-%m-%d %H:%M:%S")
                if dt_ent <= dt_est:
                    entregas_a_tiempo += 1
                else:
                    entregas_tarde += 1
            except ValueError:
                pass

    promedio_entrega = round(sum(tiempos_entrega) / len(tiempos_entrega), 1) if tiempos_entrega else 0

    return jsonify({
        "total_ordenes": len(orders),
        "estados": dict(status_counts),
        "ordenes_por_mes": por_mes_sorted,
        "promedio_entrega_dias": promedio_entrega,
        "histograma_entrega": rangos,
        "entregas_a_tiempo": entregas_a_tiempo,
        "entregas_tarde": entregas_tarde,
    })


# ---------------------------------------------------------------------------
# Endpoint: Analisis de Productos
# ---------------------------------------------------------------------------

@app.route("/api/analytics/productos", methods=["GET"])
def analytics_productos():
    """
    Analisis de productos: top categorias, distribucion de peso,
    fotos por producto, dimensiones.
    """
    products = read_csv("olist_products_dataset.csv")

    # Traduccion de categorias (PT -> EN)
    traducciones = {}
    try:
        trad_path = os.path.join(DATA_DIR, "product_category_name_translation.csv")
        with open(trad_path, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                traducciones[row["product_category_name"]] = row["product_category_name_english"]
    except Exception:
        pass

    # Top 15 categorias
    cats = Counter(p["product_category_name"] for p in products if p["product_category_name"])
    top_categorias = dict(cats.most_common(15))

    # Distribucion de peso (agrupado en rangos de gramos)
    pesos = []
    rangos_peso = {"0-500g": 0, "500g-1kg": 0, "1-2kg": 0, "2-5kg": 0, "5-10kg": 0, "10kg+": 0}
    for p in products:
        w = p.get("product_weight_g", "")
        if w:
            try:
                w = int(w)
                pesos.append(w)
                if w <= 500: rangos_peso["0-500g"] += 1
                elif w <= 1000: rangos_peso["500g-1kg"] += 1
                elif w <= 2000: rangos_peso["1-2kg"] += 1
                elif w <= 5000: rangos_peso["2-5kg"] += 1
                elif w <= 10000: rangos_peso["5-10kg"] += 1
                else: rangos_peso["10kg+"] += 1
            except ValueError:
                pass

    # Promedio de fotos por producto
    fotos = [int(p["product_photos_qty"]) for p in products if p.get("product_photos_qty")]
    promedio_fotos = round(sum(fotos) / len(fotos), 1) if fotos else 0

    # Distribucion de fotos
    dist_fotos = Counter(int(p["product_photos_qty"]) for p in products if p.get("product_photos_qty"))
    dist_fotos_sorted = dict(sorted(dist_fotos.items()))

    # Productos con descripcion mas larga vs corta
    desc_lengths = [int(p["product_description_lenght"]) for p in products if p.get("product_description_lenght")]
    promedio_desc = round(sum(desc_lengths) / len(desc_lengths)) if desc_lengths else 0

    peso_promedio = round(sum(pesos) / len(pesos)) if pesos else 0

    return jsonify({
        "total_productos": len(products),
        "total_categorias": len(cats),
        "top_categorias": top_categorias,
        "traducciones": traducciones,
        "rangos_peso": rangos_peso,
        "peso_promedio_g": peso_promedio,
        "promedio_fotos": promedio_fotos,
        "distribucion_fotos": dist_fotos_sorted,
        "promedio_largo_descripcion": promedio_desc,
    })


# ---------------------------------------------------------------------------
# Endpoint: Analisis de Items de Orden (precios y envio)
# ---------------------------------------------------------------------------

@app.route("/api/analytics/items", methods=["GET"])
def analytics_items():
    """
    Analisis de items: distribucion de precios, costos de envio,
    relacion precio-envio, top productos mas caros.
    """
    items = read_csv("olist_order_items_dataset.csv")

    precios = []
    envios = []
    for it in items:
        try:
            p = float(it["price"])
            f = float(it["freight_value"])
            precios.append(p)
            envios.append(f)
        except (ValueError, KeyError):
            pass

    # Rangos de precio
    rangos_precio = {
        "$0-25": 0, "$25-50": 0, "$50-100": 0,
        "$100-200": 0, "$200-500": 0, "$500+": 0
    }
    for p in precios:
        if p <= 25: rangos_precio["$0-25"] += 1
        elif p <= 50: rangos_precio["$25-50"] += 1
        elif p <= 100: rangos_precio["$50-100"] += 1
        elif p <= 200: rangos_precio["$100-200"] += 1
        elif p <= 500: rangos_precio["$200-500"] += 1
        else: rangos_precio["$500+"] += 1

    # Rangos de costo de envio
    rangos_envio = {
        "$0-10": 0, "$10-20": 0, "$20-30": 0,
        "$30-50": 0, "$50-100": 0, "$100+": 0
    }
    for f in envios:
        if f <= 10: rangos_envio["$0-10"] += 1
        elif f <= 20: rangos_envio["$10-20"] += 1
        elif f <= 30: rangos_envio["$20-30"] += 1
        elif f <= 50: rangos_envio["$30-50"] += 1
        elif f <= 100: rangos_envio["$50-100"] += 1
        else: rangos_envio["$100+"] += 1

    # Porcentaje de envio sobre precio (ratio)
    ratios = []
    for it in items:
        try:
            p = float(it["price"])
            f = float(it["freight_value"])
            if p > 0:
                ratios.append(round(f / p * 100, 1))
        except (ValueError, KeyError, ZeroDivisionError):
            pass

    # Distribucion del ratio envio/precio
    rangos_ratio = {"0-10%": 0, "10-20%": 0, "20-30%": 0, "30-50%": 0, "50-100%": 0, "100%+": 0}
    for r in ratios:
        if r <= 10: rangos_ratio["0-10%"] += 1
        elif r <= 20: rangos_ratio["10-20%"] += 1
        elif r <= 30: rangos_ratio["20-30%"] += 1
        elif r <= 50: rangos_ratio["30-50%"] += 1
        elif r <= 100: rangos_ratio["50-100%"] += 1
        else: rangos_ratio["100%+"] += 1

    # Ingreso total y envio total
    ingreso_total = round(sum(precios), 2)
    envio_total = round(sum(envios), 2)

    # Scatter data: muestra de precio vs envio (150 puntos)
    scatter_sample = []
    sample_indices = random.sample(range(len(items)), min(150, len(items)))
    for i in sample_indices:
        try:
            scatter_sample.append({
                "precio": float(items[i]["price"]),
                "envio": float(items[i]["freight_value"]),
            })
        except (ValueError, KeyError):
            pass

    return jsonify({
        "total_items": len(items),
        "ingreso_total": ingreso_total,
        "envio_total": envio_total,
        "precio_promedio": round(sum(precios) / len(precios), 2) if precios else 0,
        "envio_promedio": round(sum(envios) / len(envios), 2) if envios else 0,
        "precio_max": max(precios) if precios else 0,
        "envio_max": max(envios) if envios else 0,
        "rangos_precio": rangos_precio,
        "rangos_envio": rangos_envio,
        "rangos_ratio_envio": rangos_ratio,
        "scatter_precio_envio": scatter_sample,
    })


# ---------------------------------------------------------------------------
# Endpoint: Analisis de Geolocalizacion
# ---------------------------------------------------------------------------

@app.route("/api/analytics/geo", methods=["GET"])
def analytics_geo():
    """
    Analisis de geolocalizacion: distribucion por estado,
    top ciudades, datos para mapa de calor.
    """
    geo = read_csv("olist_geolocation_dataset.csv", limit=50000)

    # Distribucion por estado
    estados = Counter(g["geolocation_state"] for g in geo if g.get("geolocation_state"))
    top_estados = dict(estados.most_common(15))

    # Top 20 ciudades
    ciudades = Counter(g["geolocation_city"] for g in geo if g.get("geolocation_city"))
    top_ciudades = dict(ciudades.most_common(20))

    # Puntos para mapa (muestra de coordenadas, 1 por cada 50)
    puntos_mapa = []
    for i, g in enumerate(geo):
        if i % 50 == 0:
            try:
                puntos_mapa.append({
                    "lat": float(g["geolocation_lat"]),
                    "lng": float(g["geolocation_lng"]),
                    "city": g["geolocation_city"],
                    "state": g["geolocation_state"],
                })
            except (ValueError, KeyError):
                pass

    # Conteo por estado para el mapa (con coordenada promedio)
    state_coords = defaultdict(lambda: {"lats": [], "lngs": [], "count": 0})
    for g in geo:
        st = g.get("geolocation_state", "")
        if st:
            try:
                state_coords[st]["lats"].append(float(g["geolocation_lat"]))
                state_coords[st]["lngs"].append(float(g["geolocation_lng"]))
                state_coords[st]["count"] += 1
            except ValueError:
                pass

    estados_mapa = []
    for st, data in state_coords.items():
        if data["lats"]:
            estados_mapa.append({
                "state": st,
                "lat": round(sum(data["lats"]) / len(data["lats"]), 4),
                "lng": round(sum(data["lngs"]) / len(data["lngs"]), 4),
                "count": data["count"],
            })

    estados_mapa.sort(key=lambda x: x["count"], reverse=True)

    return jsonify({
        "total_registros": len(geo),
        "total_estados": len(estados),
        "total_ciudades": len(ciudades),
        "top_estados": top_estados,
        "top_ciudades": top_ciudades,
        "puntos_mapa": puntos_mapa[:200],
        "estados_mapa": estados_mapa,
    })


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 55)
    print("  API REST - Data Warehouse Simulation")
    print("=" * 55)
    print()
    print("Endpoints disponibles:")
    print("  GET /api/datos              - Datos crudos (paginado)")
    print("  GET /api/datos/resumen      - Estadisticas generales")
    print("  GET /api/datos/sensores     - Sensores UDP parseados")
    print("  GET /api/analytics/ordenes  - Analisis de ordenes")
    print("  GET /api/analytics/productos- Analisis de productos")
    print("  GET /api/analytics/items    - Precios y costos de envio")
    print("  GET /api/analytics/geo      - Geolocalizacion")
    print()
    app.run(host="0.0.0.0", port=5000, debug=True)
