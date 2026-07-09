import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv(override=True)

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY", "sk-2ec7249ff5834aa786b9a43d0d084ccd")

class GroqClient:
    def __init__(self):
        self.api_key = DEEPSEEK_KEY
        self.base_url = "https://api.deepseek.com/v1/chat/completions"

    def think(self, system, user, temp=0.7, max_tok=2048):
        return self._call(system, user, temp, max_tok)

    def extract_json(self, system, user):
        resp = self._call(system + "\nResponde SOLO JSON valido, sin markdown.", user, 0.3, 4096)
        try:
            return json.loads(resp.replace("```json", "").replace("```", "").strip())
        except:
            return {}

    def _call(self, system, user, temp, max_tok):
        if not self.api_key:
            return json.dumps({"error": "sin_api_key"})
        try:
            resp = requests.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-chat",
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
            print(f"[DEEPSEEK] Error {resp.status_code}: {resp.text[:200]}")
            time.sleep(2)
        except Exception as e:
            print(f"[DEEPSEEK] Exception: {e}")
        return json.dumps({"error": "fallo_llamada"})