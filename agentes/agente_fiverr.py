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
        self.email = "shadow4stories@gmail.com"
        self.password = "aissarah"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.session.headers.update(self.headers)

    def ejecutar(self):
        resultados = {}
        resultados["login"] = self._login()
        if resultados["login"].get("status") == "ok":
            resultados["buscar_postular"] = self._buscar_y_postular()
        else:
            resultados["buscar_postular"] = self._buscar_sin_login()
        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _login(self):
        try:
            resp = self.session.get("https://www.fiverr.com/login", timeout=10)
            csrf = re.search(r'name="csrf_token" value="([^"]+)"', resp.text)
            resp2 = self.session.post("https://www.fiverr.com/login/ajax", data={
                "username_or_email": self.email,
                "password": self.password,
                "csrf_token": csrf.group(1) if csrf else ""
            }, timeout=10)
            if "error" in resp2.text.lower()[:500]:
                return {"status": "error", "detalle": "credenciales incorrectas o captcha"}
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "detalle": str(e)}

    def _buscar_y_postular(self):
        resultados = []
        queries = ["python developer", "web scraper", "automation", "bot developer", "data entry", "virtual assistant", "chatbot"]
        for q in queries:
            try:
                url = f"https://www.fiverr.com/search/gigs?query={requests.utils.quote(q)}&sort=new"
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    enlaces = re.findall(r'href="(/[^"]*gig[^"]*)"', resp.text)[:3]
                    for e in enlaces:
                        gig_url = "https://www.fiverr.com" + e
                        try:
                            rg = self.session.get(gig_url, timeout=10)
                            if rg.status_code == 200:
                                titulo = re.search(r'<title>([^<]+)</title>', rg.text)
                                t = titulo.group(1).strip()[:120] if titulo else "Gig"
                                propuesta = self.ia.think(
                                    "TOP Fiverr seller. Conviertes en propuestas.",
                                    f"Propuesta personalizada para: {t}\nSkill: {q}\n\nSaludo, entendi, entrego 24-48h desde $15, CTA contratar."
                                )
                                resultados.append({"gig": t, "skill": q, "propuesta": propuesta[:200]})
                        except:
                            continue
                time.sleep(1)
            except:
                continue
        return {"postulaciones": len(resultados), "detalle": resultados}

    def _buscar_sin_login(self):
        resultados = []
        queries = ["python developer", "web scraper", "automation", "bot developer", "data entry"]
        for query in queries[:3]:
            url = f"https://www.fiverr.com/search/gigs?query={requests.utils.quote(query)}&sort=new"
            try:
                resp = self.session.get(url, timeout=10)
                enlaces = re.findall(r'href="(/[^"]*)"', resp.text)[:5]
                for e in enlaces:
                    if "/gigs/" in e or "fiverr." in e:
                        propuesta = self.ia.think(
                            "Vendedor Fiverr.",
                            f"Propuesta para trabajo de {query}. Personalizada, ofrece $15-50, entrega 24h."
                        )
                        resultados.append({"skill": query, "propuesta": propuesta[:200]})
            except:
                continue
            time.sleep(1)
        return {"postulaciones_generadas": len(resultados), "detalle": resultados}