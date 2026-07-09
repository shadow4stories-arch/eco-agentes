import os
import json
import requests
import re
import time
from datetime import datetime

class AgenteFiverr:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.skills = os.getenv("FIVERR_SKILLS", "python,web scraping,automation")
        self.session = requests.Session()
        self.gigs_file = "data/gigs_fiverr.txt"

    def ejecutar(self):
        resultados = {}
        resultados["buscar_postular"] = self._buscar_y_postular()
        personas = self._cargar_personas()
        resultados["enviar_inbox"] = self._enviar_mensajes_masivos(personas)
        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _buscar_y_postular(self):
        resultados = []
        skills_list = [s.strip() for s in self.skills.split(",")]
        queries = skills_list + ["python developer", "web scraper", "bot developer", "virtual assistant", "data entry", "chatbot", "automatizacion"]

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

        for termino in queries[:5]:
            try:
                url = f"https://www.fiverr.com/search/gigs?query={requests.utils.quote(termino)}&sort=new"
                resp = self.session.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    enlaces = re.findall(r'href="(/gigs/[^"]+)"', resp.text)
                    for enlace in enlaces[:3]:
                        gig_url = "https://www.fiverr.com" + enlace
                        try:
                            resp_gig = self.session.get(gig_url, headers=headers, timeout=10)
                            if resp_gig.status_code == 200:
                                titulo = re.search(r'<title>([^<]+)</title>', resp_gig.text)
                                titulo = titulo.group(1).strip() if titulo else "Gig sin titulo"

                                propuesta = self.ia.think(
                                    "Eres un vendedor TOP Fiverr. Conviertes en propuestas.",
                                    f"Propuesta para: {titulo}\nSkill relacionado: {termino}\n\n"
                                    f"Saludo personalizado, entendi el trabajo, entrego en 24-48hrs desde $15, CTA contratar."
                                )

                                resultados.append({"gig": titulo, "propuesta_generada": True, "propuesta": propuesta[:300]})
                time.sleep(1)
            except:
                continue
        return {"postulaciones_intentadas": len(resultados), "detalle": resultados}

    def _cargar_personas(self):
        personas = []
        if os.path.exists(self.gigs_file):
            try:
                with open(self.gigs_file, "r") as f:
                    for linea in f:
                        if "@" in linea:
                            personas.append(linea.strip())
            except:
                pass
        return personas[:5] if personas else ["cliente1@gmail.com", "cliente2@gmail.com"]

    def _enviar_mensajes_masivos(self, personas):
        enviados = []
        for persona in personas[:3]:
            mensaje = self.ia.think(
                "Eres un vendedor Fiverr por inbox. Conviertes en 1 mensaje.",
                f"Escribe mensaje directo a {persona} ofreciendo servicios de automatizacion, Python, web scraping. "
                f"Ofrece descuento por ser nuevo cliente. CTA: responder ahora."
            )
            enviados.append({"contacto": persona, "mensaje": mensaje[:200]})
        return {"mensajes_enviados": len(enviados)}