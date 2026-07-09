import os
import json
from datetime import datetime

class AgenteVentas:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.pitch = os.getenv("SERVICE_PITCH", "Servicios de automatización profesional")

    def ejecutar(self):
        resultados = {}

        # 1. Analizar leads pendientes
        resultados["analisis_leads"] = self._analizar_pipeline()

        # 2. Secuencia de seguimiento automática
        resultados["seguimiento"] = self._generar_seguimiento()

        # 3. Estrategia de cierre
        resultados["cierre"] = self._estrategia_cierre()

        # 4. Respuesta a objeciones comunes
        resultados["objeciones"] = self._preparar_objeciones()

        return json.dumps(resultados, indent=2)

    def _analizar_pipeline(self):
        return self.ia.extract_json(
            "Eres un sales manager experto. Analizas oportunidades de venta y priorizas leads.",
            f"Basado en este pitch de servicio: '{self.pitch}'\n\n"
            f"Genera 3 tipos de lead (caliente, tibio, frío) con sus características. "
            f"Para cada uno indica: estado actual, probabilidad de cierre, y siguiente paso recomendado. "
            f"Responde JSON: {{'leads': [{{'tipo':'...','probabilidad':0-100,'siguiente_paso':'...'}}]}}"
        )

    def _generar_seguimiento(self):
        seguimientos = []

        # Seguimiento Día 1
        dia1 = self.ia.think(
            "Eres un vendedor persistente pero no molesto. Sabes exactamente cuándo y cómo dar seguimiento.",
            f"Escribe un email de seguimiento (día 1 después del primer contacto) para un lead que mostró interés en: {self.pitch[:200]}\n\n"
            f"Debe ser breve, agregar valor, e incluir un recurso útil (guía, caso de estudio). "
            f"No pedir la venta aún. Máximo 150 palabras."
        )

        # Email Día 3
        dia3 = self.ia.think(
            "Eres un vendedor consultivo. Sabes crear urgencia sin ser agresivo.",
            f"Escribe email de seguimiento día 3. El lead no respondió aún. "
            f"Debe: mencionar una oferta por tiempo limitado, compartir testimonio breve de cliente satisfecho, "
            f"y preguntar si hay dudas. Máximo 120 palabras."
        )

        # Email Día 7 (último intento)
        dia7 = self.ia.think(
            "Eres un vendedor que cierra tratos. Conviertes leads fríos en clientes.",
            f"Email final de cierre para lead que no ha respondido. "
            f"Debe: crear un poco de urgencia, ofrecer una llamada de 15 minutos sin compromiso, "
            f"y dejar la puerta abierta. Máximo 100 palabras. Asunto impactante."
        )

        seguimientos = {
            "dia1": dia1[:300],
            "dia3": dia3[:300],
            "dia7": dia7[:300]
        }

        return seguimientos

    def _estrategia_cierre(self):
        return self.ia.think(
            "Eres un negociador experto. Cierras ventas de servicios profesionales con alto ticket.",
            f"Dame 5 técnicas de cierre efectivas para: {self.pitch[:100]}\n"
            f"Para cada técnica: nombre, cuándo usarla, guión exacto a decir. "
            f"Las técnicas deben funcionar para ventas B2B de servicios tecnológicos."
        )

    def _preparar_objeciones(self):
        objeciones = self.ia.extract_json(
            "Eres un experto en manejo de objeciones en ventas B2B.",
            f"Para el servicio: {self.pitch[:100]}\n\n"
            f"Genera las 5 objeciones más comunes y sus respuestas. "
            f"Responde JSON: {{'objeciones': [{{'objecion':'...','respuesta':'...','tecnica':'...'}}]}}"
        )
        return objeciones