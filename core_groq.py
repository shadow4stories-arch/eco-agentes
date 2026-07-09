import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

MODELS_PRIORIDAD = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "gemma2-9b-it",
    "llama3-8b-8192"
]

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.modelo_activo = None
        self.usar_simulacion = False
        self._iniciar()

    def _iniciar(self):
        if not self.api_key or self.api_key == "tu_api_key_de_groq_aqui":
            self.usar_simulacion = True
            print("[GROQ] API key no configurada. Usando simulación local.")
            return
        # Probar modelos hasta encontrar uno activo
        for modelo in MODELS_PRIORIDAD:
            try:
                resp = requests.post(
                    self.base_url,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={
                        "model": modelo,
                        "messages": [{"role": "user", "content": "ping"}],
                        "max_tokens": 1
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    self.modelo_activo = modelo
                    print(f"[GROQ] Conectado con modelo: {modelo}")
                    return
                else:
                    print(f"[GROQ] Modelo {modelo} no disponible ({resp.status_code})")
            except:
                continue
        self.usar_simulacion = True
        print("[GROQ] No se pudo conectar con Groq. Usando simulación local.")

    def _simular_respuesta(self, system_prompt, user_prompt, es_json=False):
        tema = user_prompt[:120].replace("\n", " ").strip()
        if es_json:
            return json.dumps({
                "simulado": True,
                "mensaje": "API de IA no configurada. Configura GROQ_API_KEY en .env para activar IA real.",
                "tema": tema[:60]
            })
        return f"[SIMULACIÓN LOCAL] Análisis generado para: {tema}...\n\nPara activar la IA real, configura GROQ_API_KEY en el archivo .env"

    def _call(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2048, es_json=False):
        if self.usar_simulacion:
            return self._simular_respuesta(system_prompt, user_prompt, es_json)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.modelo_activo,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        for attempt in range(2):
            try:
                resp = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                elif resp.status_code == 429:
                    time.sleep(15)
                    continue
                else:
                    print(f"[GROQ] Error {resp.status_code}. Cambiando a simulación.")
                    self.usar_simulacion = True
                    return self._simular_respuesta(system_prompt, user_prompt, es_json)
            except Exception as e:
                print(f"[GROQ] Exception: {e}")
                time.sleep(5)
        self.usar_simulacion = True
        return self._simular_respuesta(system_prompt, user_prompt, es_json)

    def think(self, system, user, temp=0.7):
        return self._call(system, user, temperature=temp)

    def extract_json(self, system, user):
        resp = self._call(
            system + "\nResponde SOLO con JSON válido, sin markdown ni explicaciones.",
            user,
            temperature=0.3,
            max_tokens=4096,
            es_json=True
        )
        try:
            resp_clean = resp.replace("```json", "").replace("```", "").strip()
            return json.loads(resp_clean)
        except:
            return {}