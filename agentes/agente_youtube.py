import os
import json
from datetime import datetime

class AgenteYouTube:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.channel = os.getenv("YOUTUBE_CHANNEL_NAME", "mi_canal")
        self.niche = os.getenv("YOUTUBE_NICHE", "technology")
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")

    def ejecutar(self):
        resultados = {}

        # 1. Estrategia de contenido
        resultados["estrategia_canal"] = self._plan_canal()

        # 2. Optimizar SEO de videos existentes
        resultados["optimizar_seo"] = self._optimizar_videos()

        # 3. Generar ideas de videos cortos (#Shorts)
        resultados["ideas_shorts"] = self._generar_shorts()

        # 4. Estrategia de crecimiento
        resultados["crecimiento"] = self._estrategia_crecimiento()

        # 5. Generar thumbnail descriptions
        resultados["thumbnails"] = self._generar_thumbnails()

        return json.dumps(resultados, indent=2)

    def _plan_canal(self):
        return self.ia.think(
            "Eres un estratega de YouTube que ha hecho crecer canales desde 0 a 100k suscriptores.",
            f"Crea un plan de contenido de 2 semanas para un canal sobre '{self.niche}'. "
            f"Incluye: 4 ideas de videos principales, 2 shorts, "
            f"estrategia de títulos (clickbait ético), y programación de publicación. "
            f"Considera tendencias actuales de 2026."
        )

    def _optimizar_videos(self):
        yt_dir = "output/youtube_scripts"
        optimizados = []

        if os.path.exists(yt_dir):
            for archivo in os.listdir(yt_dir)[:2]:
                filepath = os.path.join(yt_dir, archivo)
                with open(filepath, "r", encoding="utf-8") as f:
                    contenido = f.read()

                optimizacion = self.ia.extract_json(
                    "Eres un experto en SEO de YouTube. Optimizas videos para máximo alcance.",
                    f"Analiza este script de YouTube y dame:\n"
                    f"1. Título optimizado (máximo 60 caracteres)\n"
                    f"2. 3 tags principales\n"
                    f"3. Mejores momentos del video (timestamps sugeridos)\n"
                    f"4. CTA mejorado\n\n{contenido[:2000]}\n\n"
                    f"Responde JSON: {{'titulo':'...','tags':[],'timestamps':[],'cta':'...'}}"
                )

                if self.mode == "live":
                    meta_path = filepath.replace(".txt", "_yt_seo.json")
                    with open(meta_path, "w") as f:
                        json.dump(optimizacion, f, indent=2)

                optimizados.append({"archivo": archivo, "optimizacion": optimizacion})

        return optimizados if optimizados else "No hay scripts para optimizar"

    def _generar_shorts(self):
        ideas = self.ia.extract_json(
            "Eres un creador de YouTube Shorts virales. Sabes qué contenido funciona en formato vertical.",
            f"Genera 5 ideas para YouTube Shorts sobre '{self.niche}' que tengan potencial viral. "
            f"Cada Short debe durar 15-30 segundos con un hook fuerte en los primeros 2 segundos. "
            f"Responde JSON: {{'shorts':[{{'titulo':'...','hook':'...','contenido':'...','hashtags':'...'}}]}}"
        )
        return ideas

    def _estrategia_crecimiento(self):
        return self.ia.think(
            "Eres un growth hacker de YouTube. Conoces todos los trucos para crecer orgánicamente.",
            f"Dame una estrategia de crecimiento para un canal nuevo de '{self.niche}' en 2026. "
            f"Incluye: colaboraciones, comunidad, frecuencia de publicación, "
            f"cómo aprovechar tendencias, y tácticas para conseguir los primeros 1000 suscriptores rápido."
        )

    def _generar_thumbnails(self):
        return self.ia.think(
            "Eres un diseñador de thumbnails de YouTube. Tus miniaturas consiguen CTR del 15%+.",
            f"Dame 5 descripciones detalladas de thumbnails de alto CTR para videos sobre '{self.niche}'. "
            f"Para cada thumbnail describe: imagen principal, colores, texto superpuesto (máximo 4 palabras), "
            f"expresión facial (si aplica), y composición general."
        )