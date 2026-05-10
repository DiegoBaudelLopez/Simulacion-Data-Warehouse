"""
Servidor Concurrente - Fase 2
Recibe datos de los agentes TCP y UDP simultaneamente
y los almacena en PostgreSQL (Supabase).

- TCP en puerto 12000: datos transaccionales (CSV linea por linea)
- UDP en puerto 12001: datos de telemetria (JSON de sensores)
"""

import socket
import threading
import json
import sys
import os

# Agregar el directorio actual al path para importar db_config
sys.path.insert(0, os.path.dirname(__file__))
from db_config import insertar_dato, init_table

# Configuracion del servidor
HOST = "127.0.0.1"
TCP_PORT = 12000
UDP_PORT = 12001
BUFFER_SIZE = 4096


# ---------------------------------------------------------------------------
# TCP: Manejo de clientes
# ---------------------------------------------------------------------------

def manejar_cliente_tcp(conn, addr):
    """Maneja una conexion TCP individual en su propio hilo."""
    print(f"[TCP] Cliente conectado desde {addr}")
    buffer = ""
    registros = 0

    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            # Acumular datos en buffer (TCP es stream, puede llegar parcial)
            buffer += data.decode("utf-8")

            # Procesar lineas completas
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if not line:
                    continue

                # Señal de fin de transmision
                if line == "END":
                    print(f"[TCP] Cliente {addr} envio señal END.")
                    conn.close()
                    print(f"[TCP] Cliente {addr} desconectado. {registros} registros almacenados.")
                    return

                # Insertar en base de datos
                try:
                    insertar_dato("TCP", line)
                    registros += 1
                    if registros % 100 == 0:
                        print(f"[TCP] {addr} -> {registros} registros almacenados...")
                except Exception as e:
                    print(f"[TCP] Error al insertar: {e}")

    except ConnectionResetError:
        print(f"[TCP] Cliente {addr} se desconecto abruptamente.")
    except Exception as e:
        print(f"[TCP] Error con cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"[TCP] Conexion con {addr} cerrada. Total: {registros} registros.")


def escuchar_tcp():
    """Hilo principal que escucha conexiones TCP entrantes."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, TCP_PORT))
    server.listen(5)
    print(f"[TCP] Escuchando en {HOST}:{TCP_PORT}")

    while True:
        conn, addr = server.accept()
        # Cada cliente TCP se maneja en un hilo separado
        hilo = threading.Thread(
            target=manejar_cliente_tcp,
            args=(conn, addr),
            daemon=True,
        )
        hilo.start()


# ---------------------------------------------------------------------------
# UDP: Recepcion de telemetria
# ---------------------------------------------------------------------------

def escuchar_udp():
    """Hilo que recibe datagramas UDP continuamente."""
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, UDP_PORT))
    print(f"[UDP] Escuchando en {HOST}:{UDP_PORT}")

    count = 0
    while True:
        data, addr = server.recvfrom(BUFFER_SIZE)
        mensaje = data.decode("utf-8")

        try:
            # Validar que es JSON valido
            json.loads(mensaje)
            insertar_dato("UDP", mensaje)
            count += 1

            if count % 50 == 0:
                print(f"[UDP] {count} lecturas almacenadas...")

        except json.JSONDecodeError:
            print(f"[UDP] Dato no valido de {addr}: {mensaje[:50]}")
        except Exception as e:
            print(f"[UDP] Error al insertar: {e}")


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  SERVIDOR CONCURRENTE - Data Warehouse Simulation")
    print("=" * 60)
    print()

    # Verificar/crear tabla en la base de datos
    try:
        init_table()
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
        print("Verifica las credenciales en server/.env")
        sys.exit(1)

    # Iniciar hilo TCP
    hilo_tcp = threading.Thread(target=escuchar_tcp, daemon=True)
    hilo_tcp.start()

    # Iniciar hilo UDP
    hilo_udp = threading.Thread(target=escuchar_udp, daemon=True)
    hilo_udp.start()

    print()
    print("[SERVIDOR] Listo para recibir datos.")
    print("[SERVIDOR] Presiona Ctrl+C para detener.\n")

    # Mantener el hilo principal vivo
    try:
        hilo_tcp.join()
        hilo_udp.join()
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Detenido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()
