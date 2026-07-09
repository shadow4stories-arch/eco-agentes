import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class AgenteSEO:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode

    def ejecutar(self):
        resultados = {}

        # 1. Investigación de keywords
        resultados["keywords"] = self._investigar_keywords()

        # 2. Optimizar artículos existentes
        resultados["optimizacion"] = self._optimizar_contenido_existente()

        # 3. Generar estrategia SEO
        resultados["estrategia"] = self._generar_estrategia()

        # 4. Backlinks simulados (scraping de oportunidades)
        resultados["oportunidades_backlinks"] = self._buscar_oportunidades_backlinks()

        return json.dumps(resultados, indent=2)

    def _investigar_keywords(self):
        topic = os.getenv("BLOG_TOPIC", "technology automation")

        keywords_data = self.ia.extract_json(
            "Eres un investigador SEO experto. Conoces las keywords de alto valor y bajo competencia.",
            f"Para el nicho '{topic}', genera:\n"
            f"1. 5 keywords principales con alto volumen de búsqueda\n"
            f"2. 5 keywords long-tail (fáciles de posicionar)\n"
            f"3. 3 preguntas frecuentes que la gente busca\n"
            f"Responde JSON: {{'principales':[{{'keyword':'...'}}], 'long_tail':[{{'keyword':'...','dificultad':'baja/media'}}], 'preguntas':['...']}}"
        )
        return keywords_data

    def _optimizar_contenido_existente(self):
        blog_dir = "output/blogs"
        if not os.path.exists(blog_dir):
            return "No hay artículos para optimizar aún"

        optimizados = []
        for archivo in os.listdir(blog_dir)[:3]:
            filepath = os.path.join(blog_dir, archivo)
            with open(filepath, "r", encoding="utf-8") as f:
                contenido = f.read()

            sugerencias = self.ia.think(
                "Eres un auditor SEO. Identificas exactamente qué mejorar para rankear mejor en Google.",
                f"Analiza este artículo y da sugerencias SEO específicas:\n\n{contenido[:3000]}\n\n"
                f"Indica: meta description sugerida, densidad de keywords, enlaces internos sugeridos, "
                f"mejoras de legibilidad, y un título alternativo más optimizado."
            )

            if self.mode == "live":
                meta_path = filepath.replace(".txt", "_meta_seo.txt")
                with open(meta_path, "w", encoding="utf-8") as f:
                    f.write(sugerencias)
                optimizados.append({"archivo": archivo, "meta_seo": meta_path})
            else:
                optimizados.append({"archivo": archivo, "simulado": True})

        return optimizados

    def _generar_estrategia(self):
        topic = os.getenv("BLOG_TOPIC", "technology automation")
        return self.ia.think(
            "Eres un estratega SEO que ha posicionado múltiples sitios en primera página de Google.",
            f"Crea un plan SEO completo de 30 días para un blog sobre '{topic}'. "
            f"Incluye: calendario de publicaciones, estrategia de backlinks, "
            f"optimización técnica, y métricas a seguir. Sé específico y actionable."
        )

    def _buscar_oportunidades_backlinks(self):
        topic = os.getenv("BLOG_TOPIC", "technology")
        oportunidades = []

        if self.mode == "live":
            try:
                url = f"https://www.google.com/search?q={topic}+guest+post+write+for+us"
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for link in soup.select("a")[:5]:
                        href = link.get("href", "")
                        if "http" in href:
                            oportunidades.append(href[:200])
            except:
                pass

        if not oportunidades:
            oportunidades = [
                "blog.example.com/write-for-us",
                "techmagazine.com/guest-post",
                f"{topic}blog.org/contributors"
            ]

        return {"oportunidades": oportunidades[:5]}