import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv("GROQ_API_KEY") or ""

class GroqClient:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    def think(self, system, user, temp=0.7, max_tok=2048):
        return self._call(system, user, temp, max_tok)

    def extract_json(self, system, user):
        resp = self._call(system + "\nResponde SOLO JSON valido.", user, 0.3, 4096)
        try:
            return json.loads(resp.replace("```json", "").replace("```", "").strip())
        except:
            return {}

    def _call(self, system, user, temp, max_tok):
        for modelo in ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "gemma2-9b-it", "llama3-8b-8192"]:
            try:
                resp = requests.post(
                    self.base_url,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={
                        "model": modelo,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user}
                        ],
                        "temperature": temp,
                        "max_tokens": max_tok
                    },
                    timeout=120
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                print(f"[GROQ] Modelo {modelo} fallo ({resp.status_code}): {resp.text[:100]}")
            except Exception as e:
                print(f"[GROQ] Error con {modelo}: {e}")
            time.sleep(1)
        return json.dumps({"error": "modelos_no_disponibles"})