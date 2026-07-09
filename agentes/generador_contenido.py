import os
import json
from datetime import datetime

BLOG_DIR = "output/blogs"
YT_DIR = "output/youtube_scripts"
ADSTERRA_SCRIPT = '<script src="https://www.highperformanceformat.com/333d081ccb545bd33678a0f641a00be8/invoke.js"></script>'

class GeneradorContenido:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode

    def ejecutar(self):
        topic = os.getenv("BLOG_TOPIC", "technology automation")
        niche = os.getenv("YOUTUBE_NICHE", "technology")

        # 1. Generar tema trending
        temas = self.ia.extract_json(
            "Eres un estratega de contenido viral. Generas ideas que atraen tráfico orgánico.",
            f"Dame 3 temas de tendencia en '{topic}' para artículos de blog y 2 para videos de YouTube. "
            f"Responde JSON: {{'blog': [{{'titulo':'...', 'keywords':['...']}}], 'youtube': [{{'titulo':'...', 'descripcion':'...'}}]}}"
        )

        resultados = {}
        resultados["blog"] = self._generar_articulos(temas.get("blog", []))
        resultados["youtube"] = self._generar_scripts_youtube(temas.get("youtube", []))
        return json.dumps(resultados, indent=2)

    def _generar_articulos(self, temas_blog):
        if not temas_blog:
            temas_blog = [{"titulo": "Como la automatización está cambiando los negocios en 2026", "keywords": ["automatizacion", "negocios", "ia"]}]

        articulos_generados = []
        for tema in temas_blog[:2]:
            titulo = tema.get("titulo", "Artículo automatizado")
            keywords = ", ".join(tema.get("keywords", ["tecnologia"]))

            contenido = self.ia.think(
                "Eres un copywriter experto en SEO. Escribes artículos atractivos, bien estructurados y optimizados para Google.",
                f"Escribe un artículo completo (mínimo 800 palabras) sobre: '{titulo}'. "
                f"Palabras clave: {keywords}. "
                f"Formato: Título, introducción, subtítulos H2, conclusión. Incluye llamada a la acción al final."
            )

            if self.mode == "live":
                filename = titulo.lower().replace(" ", "-").replace("?", "").replace(":", "")[:50] + ".txt"
                filepath = os.path.join(BLOG_DIR, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"Título: {titulo}\n")
                    f.write(f"Keywords: {keywords}\n")
                    f.write(f"Fecha: {datetime.now()}\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(contenido)
                    f.write(f"\n\n<div style='text-align:center;margin:20px 0'>{ADSTERRA_SCRIPT}</div>")
                articulos_generados.append({"archivo": filepath, "titulo": titulo})
            else:
                articulos_generados.append({"simulado": True, "titulo": titulo, "longitud": len(contenido)})

        return articulos_generados

    def _generar_scripts_youtube(self, temas_yt):
        if not temas_yt:
            temas_yt = [{"titulo": "Automatización con IA para principiantes", "descripcion": "Guía completa 2026"}]

        scripts = []
        for tema in temas_yt[:1]:
            titulo = tema.get("titulo", "Video automatizado")
            desc = tema.get("descripcion", "")

            script = self.ia.think(
                "Eres un guionista de YouTube experto. Creas guiones que enganchan desde el segundo 1 y retienen audiencia.",
                f"Crea un guion para YouTube (8-12 minutos) sobre '{titulo}'. Descripción: {desc}. "
                f"Incluye: hook inicial, desarrollo, resumen, llamado a la acción (suscribirse, comentar). "
                f"Agrega notas de producción (qué mostrar en pantalla en cada momento)."
            )

            descripcion_video = self.ia.think(
                "Eres experto en SEO de YouTube.",
                f"Escribe una descripción optimizada y tags para el video: '{titulo}'. Incluye hashtags."
            )

            if self.mode == "live":
                filename = titulo.lower().replace(" ", "-")[:40] + ".txt"
                filepath = os.path.join(YT_DIR, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"Título: {titulo}\n")
                    f.write(f"Descripción SEO:\n{descripcion_video}\n\n")
                    f.write(f"{'='*60}\n")
                    f.write(script)
                scripts.append({"archivo": filepath, "titulo": titulo})
            else:
                scripts.append({"simulado": True, "titulo": titulo})

        return scripts