import os
import json
from datetime import datetime
from gtts import gTTS
import json

SHORTS_DIR = "output/shorts"
os.makedirs(SHORTS_DIR, exist_ok=True)

class ShortGenerator:
    def __init__(self, ia):
        self.ia = ia
        self.mode = os.getenv("MODE", "dry_run")

    def ejecutar(self):
        return json.dumps(self.generar_short(), indent=2, ensure_ascii=False)

    def generar_short(self, tema=None):
        if not tema:
            tema = "automatizacion con IA"
        idea = self.ia.extract_json(
            "Creador de Shorts virales. Hook en 2 segundos.",
            f"Idea de Short sobre '{tema}'. JSON: {{'titulo':'...','guion':'...','hashtags':'...'}}"
        )
        titulo = idea.get("titulo", f"Automatizacion con IA {datetime.now()}")
        guion = idea.get("guion", "Descubre como la IA esta cambiando el mundo.")
        hashtags = idea.get("hashtags", "#IA #automatizacion")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = {
            "titulo": titulo,
            "guion": guion,
            "hashtags": hashtags,
            "archivo_audio": "",
            "archivo_video": ""
        }

        try:
            tts = gTTS(text=guion, lang="es", slow=False)
            audio_path = os.path.join(SHORTS_DIR, f"short_{timestamp}.mp3")
            tts.save(audio_path)
            output["archivo_audio"] = audio_path
        except Exception as e:
            output["error_audio"] = str(e)

        with open(os.path.join(SHORTS_DIR, f"short_{timestamp}.json"), "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return output