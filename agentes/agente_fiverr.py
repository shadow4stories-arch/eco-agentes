import os
import json
import requests
import re

class AgenteFiverr:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.email = "shadow4stories@gmail.com"
        self.skills = os.getenv("FIVERR_SKILLS", "python,web scraping,automation")
        self.session = requests.Session()

    def ejecutar(self):
        resultados = {}
        resultados["busqueda"] = self._buscar_trabajos()
        resultados["propuestas"] = self._generar_propuestas(resultados["busqueda"])
        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _buscar_trabajos(self):
        trabajos = []
        skills_list = [s.strip() for s in self.skills.split(",")]
        queries = skills_list + ["python developer", "web scraper", "bot developer", "virtual assistant"]

        for termino in queries[:5]:
            try:
                url = f"https://www.fiverr.com/search/gigs?query={requests.utils.quote(termino)}&sort=new"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                           "Accept": "text/html,application/xhtml+xml"}
                resp = self.session.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    gigs = re.findall(r'<a[^>]*href="/gigs/[^"]*"[^>]*>([^<]+)</a>', resp.text)
                    for gig in gigs[:5]:
                        texto = gig.strip()
                        if texto and len(texto) > 20:
                            trabajos.append({"titulo": texto[:200], "skill": termino})
            except:
                continue

        if not trabajos:
            for skill in skills_list[:3]:
                trabajos.append({"titulo": f"Necesito {skill} urgente para proyecto freelance", "skill": skill})
        return trabajos

    def _generar_propuestas(self, trabajos):
        propuestas = []
        for trabajo in trabajos[:5]:
            propuesta = self.ia.think(
                "Eres un vendedor TOP en Fiverr. Tus propuestas convierten al 40%+ de los clientes.",
                f"Escribe propuesta personalizada para:\nTitulo: {trabajo.get('titulo')}\nSkill: {trabajo.get('skill')}\n\n"
                f"Debe incluir: saludo personalizado, que entendiste el trabajo, entrega rapida 24-48hrs, "
                f"precio desde $15, y CTA claro de contratar. Max 200 palabras."
            )
            propuestas.append({"trabajo": trabajo.get("titulo", "")[:80], "propuesta": propuesta[:400]})
        return propuestas