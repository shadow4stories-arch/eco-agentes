"""
ECO-AGENTES: Sistema Autónomo de Agentes de IA
Ejecuta un ciclo completo manualmente para probar el sistema.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "dry_run")

def main():
    print("=" * 60)
    print("  ECO-AGENTES v1.0 - Sistema Autónomo de Agentes")
    print("=" * 60)
    print(f"  Modo: {MODE}")
    print()

    from core_groq import GroqClient
    ia = GroqClient()

    from agentes.generador_contenido import GeneradorContenido
    from agentes.agente_fiverr import AgenteFiverr
    from agentes.agente_seo import AgenteSEO
    from agentes.agente_local import AgenteLocal
    from agentes.agente_ventas import AgenteVentas
    from agentes.agente_youtube import AgenteYouTube
    from agentes.agente_blogger import AgenteBlogger
    from agentes.agente_email import AgenteEmail

    agentes = [
        ("Generador de Contenido", GeneradorContenido(ia, MODE)),
        ("Agente Fiverr", AgenteFiverr(ia, MODE)),
        ("Agente SEO", AgenteSEO(ia, MODE)),
        ("Agente Local", AgenteLocal(ia, MODE)),
        ("Agente Ventas", AgenteVentas(ia, MODE)),
        ("Agente YouTube", AgenteYouTube(ia, MODE)),
        ("Agente Blogger", AgenteBlogger(ia, MODE)),
        ("Agente Email", AgenteEmail(ia, MODE)),
    ]

    for nombre, agente in agentes:
        print(f"\n--- Ejecutando: {nombre} ---")
        try:
            resultado = agente.ejecutar()
            print(f"[OK] {nombre}")
            # Mostrar preview del resultado
            if len(resultado) > 500:
                print(f"     Preview: {resultado[:500]}...")
            else:
                print(f"     Resultado: {resultado}")
        except Exception as e:
            print(f"[ERROR] {nombre}: {e}")

    print("\n" + "=" * 60)
    print("  CICLO COMPLETADO")
    print("  Revisa la carpeta 'output/' para ver los resultados")
    print("  Para modo autónomo continuo: python orquestador.py")
    print("=" * 60)


if __name__ == "__main__":
    main()