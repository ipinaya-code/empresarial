import asyncio
import httpx
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import models
from app.database import SessionLocal

API_URL = "http://127.0.0.1:8000"
LOG_FILE = PROJECT_ROOT / "logs" / "concurrencia.log"

async def make_request(client, url, payload):
    try:
        response = await client.post(url, json=payload)
        return response.status_code, response.json()
    except Exception as e:
        return 500, str(e)

async def test_scenario(scenario_name, endpoint, num_requests=5):
    lines = [f"\n--- Iniciando prueba de concurrencia: {scenario_name} ---"]
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        # Reset DB
        await client.post(f"{API_URL}/reset")
        
        # Seed DB
        seed_res = await client.post(f"{API_URL}/seed")
        seed_data = seed_res.json()
        
        if "asiento_id" not in seed_data:
            lines.append(f"Error: No se pudo inicializar la base de datos {seed_data}")
            write_log(lines)
            return

        asiento_id = seed_data["asiento_id"]
        
        lines.append(f"Enviando {num_requests} solicitudes simultáneas al asiento {asiento_id}...")
        
        tasks = []
        for i in range(1, num_requests + 1):
            payload = {"usuario_id": i, "asiento_id": asiento_id}
            tasks.append(make_request(client, f"{API_URL}{endpoint}", payload))
            
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        lines.append(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")
        
        success_count = sum(1 for status, res in results if status == 200)
        error_count = num_requests - success_count
        
        with SessionLocal() as db:
            active_reservations = db.query(models.Reserva).filter(
                models.Reserva.asiento_id == asiento_id,
                models.Reserva.estado.in_([
                    models.EstadoReserva.PENDIENTE,
                    models.EstadoReserva.CONFIRMADA,
                ]),
            ).count()
            seat = db.query(models.Asiento).filter(models.Asiento.id == asiento_id).one()

        overassignments = max(0, active_reservations - 1)
        lines.append(f"Resultados ({scenario_name}):")
        lines.append(f"- Solicitudes exitosas: {success_count}")
        lines.append(f"- Solicitudes fallidas: {error_count}")
        lines.append(f"- Reservas activas persistidas: {active_reservations}")
        lines.append(f"- Sobreasignaciones persistidas: {overassignments}")
        lines.append(f"- Estado final del asiento: {seat.estado.value}")
        
        if success_count > 1:
            lines.append("ADVERTENCIA: hubo más de una respuesta exitosa.")
        elif success_count == 1:
            lines.append("ÉXITO: solo una solicitud fue aceptada.")
        else:
            lines.append("ERROR: ninguna solicitud fue aceptada.")
            
        for i, (status, res) in enumerate(results):
            lines.append(f"  Usuario {i+1} -> HTTP {status}: {res}")

        write_log(lines)
        for line in lines:
            print(line)

        if endpoint == "/reservar/seguro":
            assert active_reservations == 1, "La ruta segura debe dejar una sola reserva activa"
            assert seat.estado == models.EstadoAsiento.CONFIRMADO


def write_log(lines):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as log:
        log.write("\n".join(lines) + "\n")

async def main():
    # Wait for server to start
    await asyncio.sleep(2)
    
    # 1. Escenario Inseguro (Sin Control Transaccional)
    await test_scenario("SIN CONTROL (Condición de Carrera)", "/reservar/inseguro", 5)
    
    # 2. Escenario Seguro (Con Bloqueo Pesimista)
    await test_scenario("CON BLOQUEO PESIMISTA (SELECT FOR UPDATE)", "/reservar/seguro", 5)

if __name__ == "__main__":
    asyncio.run(main())
