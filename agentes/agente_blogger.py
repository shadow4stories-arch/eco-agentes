import os
import json
import glob
import requests

class AgenteBlogger:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.email = "shadow4stories@gmail.com"
        self.client_secret_path = "client_secret.json"
        self.token_path = "data/token_blogger.json"

    def ejecutar(self):
        resultados = {}

        if not os.path.exists(self.client_secret_path):
            resultados["error"] = "No existe client_secret.json"
            return json.dumps(resultados)

        token = self._obtener_token()
        if not token:
            resultados["status"] = "necesita autorizacion manual"
            resultados["instrucciones"] = "Ejecuta: python -c 'from agentes.agente_blogger import AgenteBlogger; from core_groq import GroqClient; a=AgenteBlogger(GroqClient(),\"live\"); a._autorizar_manual()'"
            return json.dumps(resultados, indent=2, ensure_ascii=False)

        resultados["token"] = "ok"
        articulo = self._conseguir_articulo()
        if articulo:
            resultados["publicado"] = self._publicar_blog(token, articulo)
        else:
            resultados["status"] = "sin_articulo"

        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _obtener_token(self):
        if os.path.exists(self.token_path):
            try:
                return json.load(open(self.token_path)).get("access_token")
            except:
                return None
        return None

    def _conseguir_articulo(self):
        archivos = glob.glob("output/blogs/*.txt")
        if archivos:
            with open(archivos[0], "r", encoding="utf-8") as f:
                contenido = f.read()
            titulo = contenido.split("\n")[0].replace("Titulo: ", "").strip()
            return {"titulo": titulo or "Sin titulo", "contenido": contenido[:10000]}
        contenido = self.ia.think(
            "Eres un blogger experto en tecnologia y automatizacion.",
            "Escribe un articulo completo de blog (600+ palabras) sobre automatizacion con IA para negocios. Titulo atractivo, introduccion, 3 subtitulos H2, conclusion, CTA."
        )
        return {"titulo": contenido.split("\n")[0][:80], "contenido": contenido[:10000]}

    def _publicar_blog(self, token, articulo):
        try:
            blog_id_url = "https://www.googleapis.com/blogger/v3/users/self/blogs"
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.get(blog_id_url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return {"error": f"No se pudo obtener blog: {resp.text[:200]}"}
            blogs = resp.json().get("items", [])
            if not blogs:
                blog_id = self._crear_blog(token)
                if not blog_id:
                    return {"error": "No hay blogs y no se pudo crear uno"}
            else:
                blog_id = blogs[0]["id"]

            url = f"https://www.googleapis.com/blog/v3/blogs/{blog_id}/posts"
            payload = {"kind": "blogger#post", "title": articulo["titulo"], "content": articulo["contenido"].replace("\n", "<br>")}
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                return {"publicado": True, "titulo": articulo["titulo"][:60]}
            return {"publicado": False, "error": resp.text[:200]}
        except Exception as e:
            return {"publicado": False, "error": str(e)}

    def _crear_blog(self, token):
        return None

    def _autorizar_manual(self):
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_path, ["https://www.googleapis.com/auth/blogger"])
        creds = flow.run_local_server(port=0)
        with open(self.t_path, "w") as f:
            json.dump({"access_token": creds.token, "refresh_token": creds.refresh_token}, f)
        print("Token guardado en", self.t_path)