import os
import json
import glob
from datetime import datetime

class AgenteBlogger:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.email = "shadow4stories@gmail.com"
        self.blog_id = self._obtener_blog_id()
        self.access_token = None

    def _obtener_blog_id(self):
        blogs = {
            "shadow4stories@gmail.com": "shadowtech",
            "por defecto": "techautomation2024"
        }
        return blogs.get(self.email, "shadowtech")

    def ejecutar(self):
        resultados = {}
        resultados["blog_id"] = self.blog_id

        articulo = self._conseguir_o_crear_articulo()
        if not articulo:
            return json.dumps({"status": "sin_articulo"})

        if self.mode == "live" and self.access_token:
            resultados["publicado"] = self._publicar_api(articulo)
        else:
            resultados["articulo_generado"] = articulo["titulo"][:60]
            resultados["status"] = "listo_para_publicar"

        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _conseguir_o_crear_articulo(self):
        archivos = glob.glob("output/blogs/*.txt")
        if archivos:
            with open(archivos[0], "r", encoding="utf-8") as f:
                contenido = f.read()
            titulo = contenido.split("\n")[0].replace("Titulo: ", "").strip()
            return {"titulo": titulo or "Sin titulo", "contenido": contenido[:10000]}
        else:
            contenido = self.ia.think(
                "Eres un blogger experto en tecnologia y automatizacion.",
                "Escribe un articulo completo de blog (600+ palabras) sobre automatizacion con IA para negocios. "
                "Titulo atractivo, introduccion, 3 subtitulos H2, conclusion, CTA."
            )
            titulo = contenido.split("\n")[0][:80]
            return {"titulo": titulo, "contenido": contenido[:10000]}

    def _publicar_api(self, articulo):
        import requests
        try:
            url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/"
            headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
            payload = {
                "kind": "blogger#post",
                "title": articulo["titulo"],
                "content": articulo["contenido"].replace("\n", "<br>")
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                return {"publicado": True, "titulo": articulo["titulo"][:60]}
            return {"publicado": False, "error": resp.text[:200]}
        except Exception as e:
            return {"publicado": False, "error": str(e)}