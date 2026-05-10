"""
Agente Transaccional (TCP)
Simula un sistema critico que envia datos de ordenes linea por linea
a traves de una conexion TCP confiable.
"""

import socket
import csv
import time
import os
import sys

# Configuracion
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12000
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Archivos CSV a enviar (los mas relevantes para el warehouse)
CSV_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
]

DELAY_SECONDS = 1  # Pausa entre envios para simular trafico real


def send_csv_file(sock, filepath):
    """Lee un CSV y envia cada fila como una linea de texto por TCP."""
    filename = os.path.basename(filepath)
    print(f"[TCP] Enviando archivo: {filename}")

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # Primera linea = encabezados
        # Enviar encabezado con prefijo del nombre de archivo
        header_line = f"FILE:{filename}|{','.join(header)}"
        sock.sendall((header_line + "\n").encode("utf-8"))
        print(f"  -> Encabezados: {','.join(header[:3])}...")

        count = 0
        for row in reader:
            line = ",".join(row)
            message = f"DATA:{filename}|{line}\n"
            sock.sendall(message.encode("utf-8"))
            count += 1

            if count % 100 == 0:
                print(f"  -> {count} registros enviados...")

            time.sleep(DELAY_SECONDS)

    print(f"[TCP] Archivo {filename} completado: {count} registros enviados.")
    return count


def main():
    total = 0

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[TCP] Conectando a {SERVER_HOST}:{SERVER_PORT}...")
        sock.connect((SERVER_HOST, SERVER_PORT))
        print("[TCP] Conexion establecida.")

        for csv_file in CSV_FILES:
            filepath = os.path.join(DATA_DIR, csv_file)
            if not os.path.exists(filepath):
                print(f"[TCP] Archivo no encontrado: {filepath}, saltando.")
                continue
            total += send_csv_file(sock, filepath)

        # Señal de fin de transmision
        sock.sendall("END\n".encode("utf-8"))
        print(f"\n[TCP] Transmision finalizada. Total: {total} registros.")

    except ConnectionRefusedError:
        print(f"[TCP] Error: No se pudo conectar a {SERVER_HOST}:{SERVER_PORT}.")
        print("  Asegurate de que el servidor (Fase 2) este corriendo.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[TCP] Transmision interrumpida por el usuario.")
    finally:
        sock.close()
        print("[TCP] Conexion cerrada.")


if __name__ == "__main__":
    main()
