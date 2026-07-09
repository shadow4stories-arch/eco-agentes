import os
import json

CIUDADES_ESPANA = [
    "Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Malaga",
    "Zaragoza", "Murcia", "Palma", "Granada", "Alicante", "Cordoba",
    "Valladolid", "Vigo", "Gijon", "Santander", "Pamplona", "San Sebastian",
    "La Coruna", "Toledo", "Badajoz", "Salamanca", "Huelva", "Almeria",
    "Cadiz", "Jaen", "Leon", "Lugo", "Ourense", "Oviedo"
]

class AgenteLocal:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.service = os.getenv("LOCAL_SERVICE", "desarrollo web,automatizacion")

    def ejecutar(self):
        resultados = {}
        resultados["leads"] = self._encontrar_leads()
        resultados["propuestas_email"] = self._generar_propuestas(resultados["leads"])
        resultados["estrategia_nacional"] = self._plan_nacional()
        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _encontrar_leads(self):
        leads = []
        servicios = [s.strip() for s in self.service.split(",")]

        for servicio in servicios[:2]:
            for ciudad in CIUDADES_ESPANA[:5]:
                lead = self.ia.extract_json(
                    "Eres un generador de leads B2B realista para toda Espana. Conoces el mercado espanol.",
                    f"Genera un lead B2B realista en {ciudad} que necesite {servicio}. "
                    f"Incluye: 'nombre' (nombre de negocio realista), 'tipo' (sector), "
                    f"'tamano' (pequena/mediana/grande), 'necesidad' (por que necesitan {servicio}), "
                    f"'web' (su posible sitio web). Responde SOLO JSON."
                )
                if lead and lead.get("nombre"):
                    lead["ciudad"] = ciudad
                    lead["servicio"] = servicio
                    leads.append(lead)
                if len(leads) >= 8:
                    break
            if len(leads) >= 8:
                break
        return leads

    def _generar_propuestas(self, leads):
        propuestas = []
        for lead in leads[:5]:
            nombre = lead.get("nombre", "Cliente potencial")
            necesidad = lead.get("necesidad", "automatizar procesos")
            ciudad = lead.get("ciudad", "Espana")

            propuesta = self.ia.think(
                "Eres un vendedor B2B experto en Espana. Ofreces servicios de desarrollo web, automatizacion e IA. Conviertes leads en clientes con correos persuasivos.",
                f"Escribe un correo de ventas COMPLETO:\n"
                f"Empresa: {nombre}\nCiudad: {ciudad}\nNecesidad: {necesidad}\n\n"
                f"Incluye: Asunto atractivo, Saludo, Propuesta de valor, Caso de exito breve, "
                f"Oferta: PRIMERA CONSULTORIA GRATIS, CTA claro, Firma: Shadow Tech | Automatizacion con IA. "
                f"Maximo 250 palabras."
            )

            propuestas.append({
                "empresa": nombre,
                "ciudad": ciudad,
                "propuesta": propuesta[:500]
            })
        return propuestas

    def _plan_nacional(self):
        return self.ia.think(
            "Eres un estratega de ventas B2B para toda Espana.",
            "Crea una estrategia de prospeccion nacional para conseguir clientes de automatizacion e IA en toda Espana. "
            "Incluye: canales (Google My Business, LinkedIn, directorios espanoles), "
            "argumento de venta, precio sugerido (EUR), y plan de seguimiento semanal."
        )