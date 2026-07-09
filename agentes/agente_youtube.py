import os
import json
import time
import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class AgenteYouTube:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.email = "shadow4stories@gmail.com"
        self.password = os.getenv("YOUTUBE_PASSWORD", "aissarah")

    def ejecutar(self):
        resultados = {}
        if self.mode != "live":
            return json.dumps({"status": "dry_run"})

        resultados["short"] = self._generar_short()

        chrome_ops = Options()
        chrome_ops.add_argument("--headless=new")
        chrome_ops.add_argument("--no-sandbox")
        chrome_ops.add_argument("--disable-dev-shm-usage")
        chrome_ops.add_argument("--window-size=720,1280")
        chrome_ops.binary_location = "/usr/bin/chromium-browser"

        try:
            driver = webdriver.Chrome(options=chrome_ops)
        except:
            driver = webdriver.Chrome(options=chrome_ops)

        try:
            driver.get("https://accounts.google.com/signin")
            time.sleep(2)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))).send_keys(self.email + Keys.RETURN)
            time.sleep(3)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))).send_keys(self.password + Keys.RETURN)
            time.sleep(5)

            driver.get("https://studio.youtube.com")
            time.sleep(5)

            try:
                driver.find_element(By.XPATH, "//ytcp-button[contains(.,'Create')]").click()
            except:
                driver.find_element(By.XPATH, "//*[contains(text(),'CREATE')]").click()
            time.sleep(2)
            try:
                driver.find_element(By.XPATH, "//ytcp-ve[contains(.,'Upload video')]").click()
            except:
                driver.find_element(By.XPATH, "//*[contains(text(),'Upload')]").click()
            time.sleep(3)

            resultados["upload"] = {
                "status": "short_generado",
                "titulo": resultados["short"].get("titulo", "Short automatizado"),
                "audio": resultados["short"].get("archivo_audio", "")
            }

            driver.quit()
            return json.dumps(resultados, indent=2, ensure_ascii=False)
        except Exception as e:
            try:
                driver.quit()
            except:
                pass
            resultados["error_upload"] = str(e)
            return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _generar_short(self):
        from agentes.short_generator import ShortGenerator
        generator = ShortGenerator(self.ia)
        short = generator.generar_short(tema="automatizacion con IA")
        with open("data/ultimo_short.json", "w") as f:
            json.dump(short, f, indent=2, ensure_ascii=False)
        return short