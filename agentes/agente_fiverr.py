import os
import json
import re
import time
import requests
from datetime import datetime

class AgenteFiverr:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.skills = os.getenv("FIVERR_SKILLS", "python,web scraping,automation")
        self.session = requests.Session()

    def ejecutar(self):
        resultados = {}
        resultados["buscar_postular"] = self._buscar_y_postular()
        resultados["enviar_propuestas_masivas"] = self._enviar_inbox_masivo()
        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _buscar_y_postular(self):
        resultados = []
        skills_list = [s.strip() for s in self.skills.split(",")]
        queries = skills_list + ["python developer", "web scraper", "bot developer", "virtual assistant", "data entry", "chatbot"]

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

        for termino in queries[:8]:
            try:
                url = f"https://www.fiverr.com/search/gigs?query={requests.utils.quote(termino)}&sort=new"
                resp = self.session.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    enlaces = re.findall(r'href="(/gigs/[^"]+)"', resp.text)
                    for enlace in enlaces[:4]:
                        gig_url = "https://www.fiverr.com" + enlace
                        try:
                            resp_gig = self.session.get(gig_url, headers=headers, timeout=10)
                            if resp_gig.status_code == 200:
                                titulo = re.search(r'<title>([^<]+)</title>', resp_gig.text)
                                titulo = titulo.group(1).strip() if titulo else "Gig sin titulo"

                                propuesta = self.ia.think(
                                    "Eres un vendedor TOP Fiverr. Tus propuestas convierten al 40%.",
                                    f"Propuesta para: {titulo}\nSkill: {termino}\n\n"
                                    f"Saludo personalizado, entendi el trabajo, entrego en 24-48hrs, "
                                    f"desde $15, revisiones ilimitadas. CTA: Contratame ahora. Max 200 pal."
                                )

                                resultados.append({
                                    "gig": titulo[:100],
                                    "skill": termino,
                                    "propuesta": propuesta[:300],
                                    "url": gig_url
                                })
                            time.sleep(0.5)
                        except:
                            continue
                time.sleep(1)
            except:
                continue
        return {"postulaciones": len(resultados), "detalle": resultados}

    def _enviar_inbox_masivo(self):
        mensajes = []
        vendedores = ["python_dev", "webscraper_pro", "automation_expert", "data_worker", "bot_creator"]
        for vendedor in vendedores[:3]:
            mensaje = self.ia.think(
                "Eres un vendedor en Fiverr contactando compradores potenciales.",
                f"Escribe mensaje directo breve ofreciendo servicios de automatizacion. "
                f"Ofrece descuento 20% primera orden. CTA: responder."
            )
            mensajes.append({"contacto": vendedor, "mensaje": mensaje[:200]})
        return {"intentos_contacto": len(mensajes)}