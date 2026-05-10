"""
Agente de Telemetria (UDP)
Simula sensores en tiempo real que generan datos aleatorios
y los envian por UDP sin garantia de entrega.
"""

import socket
import time
import random
import json
import sys
from datetime import datetime

# Configuracion
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12001
DELAY_SECONDS = 0.5  # Envios cada medio segundo
NUM_READINGS = 200   # Cantidad de lecturas a generar (ajustable)

# Sensores simulados
SENSORS = [
    {"id": "TEMP-001", "type": "temperatura", "unit": "°C", "min": 18.0, "max": 45.0},
    {"id": "HUM-001",  "type": "humedad",     "unit": "%",  "min": 20.0, "max": 95.0},
    {"id": "VEL-001",  "type": "velocidad",   "unit": "km/h", "min": 0.0, "max": 120.0},
    {"id": "PRES-001", "type": "presion",     "unit": "hPa",  "min": 980.0, "max": 1050.0},
]


def generate_reading():
    """Genera una lectura aleatoria de un sensor al azar."""
    sensor = random.choice(SENSORS)
    value = round(random.uniform(sensor["min"], sensor["max"]), 2)

    reading = {
        "sensor_id": sensor["id"],
        "type": sensor["type"],
        "value": value,
        "unit": sensor["unit"],
        "timestamp": datetime.now().isoformat(),
    }
    return reading


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[UDP] Agente de telemetria iniciado.")
    print(f"[UDP] Destino: {SERVER_HOST}:{SERVER_PORT}")
    print(f"[UDP] Generando {NUM_READINGS} lecturas con intervalo de {DELAY_SECONDS}s\n")

    count = 0
    try:
        for _ in range(NUM_READINGS):
            reading = generate_reading()
            message = json.dumps(reading)
            sock.sendto(message.encode("utf-8"), (SERVER_HOST, SERVER_PORT))

            count += 1
            print(f"  [{count}] {reading['sensor_id']} -> {reading['value']} {reading['unit']}")

            time.sleep(DELAY_SECONDS)

        print(f"\n[UDP] Transmision finalizada. Total: {count} lecturas enviadas.")

    except KeyboardInterrupt:
        print(f"\n[UDP] Interrumpido. {count} lecturas enviadas.")
    finally:
        sock.close()
        print("[UDP] Socket cerrado.")


if __name__ == "__main__":
    main()
