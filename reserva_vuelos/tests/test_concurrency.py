import asyncio
import httpx
import time

API_URL = "http://127.0.0.1:8000"

async def make_request(client, url, payload):
    try:
        response = await client.post(url, json=payload)
        return response.status_code, response.json()
    except Exception as e:
        return 500, str(e)

async def test_scenario(scenario_name, endpoint, num_requests=5):
    print(f"\n--- Iniciando prueba de concurrencia: {scenario_name} ---")
    
    async with httpx.AsyncClient() as client:
        # Reset DB
        await client.post(f"{API_URL}/reset")
        
        # Seed DB
        seed_res = await client.post(f"{API_URL}/seed")
        seed_data = seed_res.json()
        
        if "asiento_id" not in seed_data:
            print("Error: No se pudo inicializar la base de datos", seed_data)
            return

        asiento_id = seed_data["asiento_id"]
        
        print(f"Enviando {num_requests} solicitudes simultáneas al asiento {asiento_id}...")
        
        tasks = []
        for i in range(1, num_requests + 1):
            payload = {"usuario_id": i, "asiento_id": asiento_id}
            tasks.append(make_request(client, f"{API_URL}{endpoint}", payload))
            
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")
        
        success_count = sum(1 for status, res in results if status == 200)
        error_count = num_requests - success_count
        
        print(f"Resultados ({scenario_name}):")
        print(f"- Solicitudes exitosas (Reservas confirmadas): {success_count}")
        print(f"- Solicitudes fallidas (Asiento no disponible u error): {error_count}")
        
        if success_count > 1:
            print(f"⚠️ ADVERTENCIA: ¡Condición de carrera detectada! {success_count} usuarios reservaron el mismo asiento.")
        elif success_count == 1:
            print(f"✅ ÉXITO: Bloqueo transaccional funcionó correctamente. Solo 1 usuario reservó el asiento.")
        else:
            print(f"❌ ERROR: Ningún usuario pudo reservar el asiento.")
            
        for i, (status, res) in enumerate(results):
            print(f"  Usuario {i+1} -> HTTP {status}: {res}")

async def main():
    # Wait for server to start
    await asyncio.sleep(2)
    
    # 1. Escenario Inseguro (Sin Control Transaccional)
    await test_scenario("SIN CONTROL (Condición de Carrera)", "/reservar/inseguro", 5)
    
    # 2. Escenario Seguro (Con Bloqueo Pesimista)
    await test_scenario("CON BLOQUEO PESIMISTA (SELECT FOR UPDATE)", "/reservar/seguro", 5)

if __name__ == "__main__":
    asyncio.run(main())
