import os
import sys
import json
import time
import schedule
import threading
from datetime import datetime
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
from core_groq import GroqClient

# Forzar flush de stdout para que Render vea los logs
sys.stdout.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

load_dotenv(override=True)
for k, v in os.environ.items():
    if v and not k.startswith("_"):
        pass  # Render env vars ya estan en os.environ

MODE = os.getenv("MODE", "dry_run")
CYCLE_MINUTES = int(os.getenv("CYCLE_MINUTES", 60))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Eco-Agentes Running")
    def log_message(self, format, *args):
        pass

def iniciar_health_server():
    try:
        server = HTTPServer(("0.0.0.0", 10000), HealthHandler)
        server.serve_forever()
    except Exception as e:
        pass

health_thread = threading.Thread(target=iniciar_health_server, daemon=True)
health_thread.start()
time.sleep(1)

class Orquestador:
    def __init__(self):
        self.ia = GroqClient()
        self.agentes = {}
        os.makedirs("data", exist_ok=True)
        os.makedirs("output/blogs", exist_ok=True)
        os.makedirs("output/youtube_scripts", exist_ok=True)
        self.bitacora = "data/bitacora.json"
        self.estado_agentes = {}
        self._cargar_bitacora()

    def _cargar_bitacora(self):
        if os.path.exists(self.bitacora):
            with open(self.bitacora, "r") as f:
                self.estado_agentes = json.load(f)
        else:
            self.estado_agentes = {
                "generador_contenido": {"activo": True, "ultimo_ciclo": "", "tareas_completadas": 0},
                "agente_fiverr": {"activo": True, "ultimo_ciclo": "", "tareas_completadas": 0},
                "agente_seo": {"activo": True, "ultimo_ciclo": "", "tareas_completadas": 0},
                "agente_local": {"activo": True, "ultimo_ciclo": "", "tareas_completadas": 0},
                "agente_ventas": {"activo": True, "ultimo_ciclo": "", "tareas_completadas": 0},
                "agente_youtube": {"activo": True, "ultimo_ciclo": "", "tareas_completadas": 0}
            }
            self._guardar_bitacora()

    def _guardar_bitacora(self):
        with open(self.bitacora, "w") as f:
            json.dump(self.estado_agentes, f, indent=2)

    def registrar_agente(self, nombre, instancia):
        self.agentes[nombre] = instancia

    def ciclo_principal(self):
        print(f"\n{'='*60}", flush=True)
        print(f"[ORQUESTADOR] Ciclo iniciado: {datetime.now()}", flush=True)
        print(f"[ORQUESTADOR] Modo: {MODE}", flush=True)
        print(f"{'='*60}", flush=True)

        decisiones = self.ia.extract_json(
            "Eres un orquestador de agentes de IA. Decides qué agente debe ejecutar acciones en cada ciclo basado en la productividad y resultados.",
            f"Estado actual de agentes: {json.dumps(self.estado_agentes, indent=2)}\n\n"
            f"Modo: {MODE}\n"
            f"Ciclo: cada {CYCLE_MINUTES} minutos\n\n"
            f"Decide en orden de prioridad qué agentes ejecutar (máximo 3 por ciclo). "
            f"Responde JSON: {{'ejecutar': ['agente1','agente2'], 'razon': 'tu razon'}}"
        )

        ejecutar = decisiones.get("ejecutar", list(self.agentes.keys())[:3])
        print(f"[ORQUESTADOR] Agentes a ejecutar: {ejecutar}")

        for nombre_agente in ejecutar:
            if nombre_agente in self.agentes:
                try:
                    print(f"\n--- Ejecutando: {nombre_agente} ---", flush=True)
                    resultado = self.agentes[nombre_agente].ejecutar()
                    self.estado_agentes[nombre_agente]["ultimo_ciclo"] = str(datetime.now())
                    self.estado_agentes[nombre_agente]["tareas_completadas"] += 1
                    self._guardar_bitacora()
                    print(f"[OK] {nombre_agente}: {resultado[:200]}", flush=True)
                except Exception as e:
                    print(f"[ERROR] {nombre_agente}: {e}", flush=True)
            else:
                print(f"[!] Agente '{nombre_agente}' no registrado", flush=True)

        print(f"\n[ORQUESTADOR] Ciclo completado. Proximo en {CYCLE_MINUTES} minutos.\n", flush=True)

    def iniciar(self):
        print("[ORQUESTADOR] Sistema iniciado. Modo autonomo activado.")
        print(f"[ORQUESTADOR] Forzando primer ciclo inmediato...", flush=True)
        try:
            self.ciclo_principal()
        except Exception as e:
            print(f"[ORQUESTADOR] Error en primer ciclo: {e}", flush=True)
            import traceback
            traceback.print_exc()
        print(f"[ORQUESTADOR] Primer ciclo completado. Proximo en {CYCLE_MINUTES} minutos.", flush=True)
        schedule.every(CYCLE_MINUTES).minutes.do(self.ciclo_principal)
        while True:
            schedule.run_pending()
            time.sleep(30)


def main():
    orq = Orquestador()

    from agentes.generador_contenido import GeneradorContenido
    from agentes.agente_fiverr import AgenteFiverr
    from agentes.agente_seo import AgenteSEO
    from agentes.agente_local import AgenteLocal
    from agentes.agente_ventas import AgenteVentas
    from agentes.agente_youtube import AgenteYouTube
    from agentes.agente_blogger import AgenteBlogger
    from agentes.agente_email import AgenteEmail
    from agentes.short_generator import ShortGenerator

    orq.registrar_agente("generador_contenido", GeneradorContenido(orq.ia, MODE))
    orq.registrar_agente("agente_fiverr", AgenteFiverr(orq.ia, MODE))
    orq.registrar_agente("agente_seo", AgenteSEO(orq.ia, MODE))
    orq.registrar_agente("agente_local", AgenteLocal(orq.ia, MODE))
    orq.registrar_agente("agente_ventas", AgenteVentas(orq.ia, MODE))
    orq.registrar_agente("agente_youtube", AgenteYouTube(orq.ia, MODE))
    orq.registrar_agente("agente_blogger", AgenteBlogger(orq.ia, MODE))
    orq.registrar_agente("agente_email", AgenteEmail(orq.ia, MODE))
    orq.registrar_agente("short_generator", ShortGenerator(orq.ia))

    orq.iniciar()

if __name__ == "__main__":
    main()