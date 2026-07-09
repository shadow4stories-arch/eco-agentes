import os
import json
import glob
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class AgenteBlogger:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.email = "shadow4stories@gmail.com"
        self.password = os.getenv("BLOGGER_PASSWORD", "aissarah")

    def ejecutar(self):
        resultados = {}
        if self.mode != "live":
            return json.dumps({"status": "dry_run"})

        chrome_ops = Options()
        chrome_ops.add_argument("--headless=new")
        chrome_ops.add_argument("--no-sandbox")
        chrome_ops.add_argument("--disable-dev-shm-usage")
        chrome_ops.binary_location = "/usr/bin/chromium-browser"

        try:
            driver = webdriver.Chrome(options=chrome_ops)
        except:
            driver = webdriver.Chrome(options=chrome_ops)

        try:
            driver.get("https://www.blogger.com")
            time.sleep(2)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))).send_keys(self.email + Keys.RETURN)
            time.sleep(3)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))).send_keys(self.password + Keys.RETURN)
            time.sleep(5)

            articulo = self._conseguir_articulo()
            if not articulo:
                resultados["status"] = "sin_articulo"
                return json.dumps(resultados)

            driver.get("https://www.blogger.com/blog/posts")
            time.sleep(3)
            try:
                driver.find_element(By.XPATH, "//div[contains(text(),'New post')]").click()
            except:
                driver.find_element(By.XPATH, "//a[contains(@href,'create-post')]").click()
            time.sleep(3)

            title_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='title'], input[aria-label*='Post title']")))
            title_input.send_keys(articulo["titulo"])

            content = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
            content.send_keys(articulo["contenido"][:5000])

            try:
                driver.find_element(By.XPATH, "//span[contains(text(),'Publish')]").click()
            except:
                driver.find_element(By.XPATH, "//div[contains(@aria-label,'Publish')]").click()
            time.sleep(3)

            driver.quit()
            return json.dumps({"publicado": True, "titulo": articulo["titulo"][:60]}, ensure_ascii=False)
        except Exception as e:
            try:
                driver.quit()
            except:
                pass
            return json.dumps({"publicado": False, "error": str(e)}, ensure_ascii=False)

    def _conseguir_articulo(self):
        archivos = glob.glob("output/blogs/*.txt")
        if archivos:
            with open(archivos[0], "r", encoding="utf-8") as f:
                contenido = f.read()
            titulo = contenido.split("\n")[0].replace("Titulo: ", "").strip()
            return {"titulo": titulo, "contenido": contenido[:10000]}
        contenido = self.ia.think(
            "Eres un blogger experto en tecnologia.",
            "Escribe articulo completo (600+ palabras) sobre automatizacion con IA para negocios."
        )
        return {"titulo": contenido.split("\n")[0][:80], "contenido": contenido[:10000]}