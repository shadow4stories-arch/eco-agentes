import os
import json
import requests
from datetime import datetime

class AgenteYouTube:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.niche = "technology automation shorts"

    def ejecutar(self):
        resultados = {}
        resultados["generar_shorts"] = self._generar_shorts()
        resultados["subir_api"] = self._subir_short_api()
        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _generar_shorts(self):
        ideas = self.ia.extract_json(
            "Eres un creador de Shorts virales de YouTube. Sabes que funciona.",
            f"Genera 3 ideas de Shorts (menos de 60 seg) sobre '{self.niche}' para el canal shadowhub. "
            f"Cada Short debe tener hook fuerte en primeros 2 segundos. "
            f"JSON: {{'shorts':[{{'titulo':'...','guion':'...','hashtags':'...'}}]}}"
        )
        return ideas.get("shorts", [])

    def _subir_por_api(self):
        if not self.api_key:
            return {"error": "Sin API key de YouTube"}
        try:
            url = "https://www.youtube.com/upload"
            headers = {"User-Agent": "Mozilla/5.0"}
            return {"status": "simulado_upload", "mensaje": "La API de YouTube requiere OAuth para subir. Los scripts estan listos en output/youtube_scripts/ para que los subas manualmente o configures OAuth."}
        except Exception as e:
            return {"error": str(e)}