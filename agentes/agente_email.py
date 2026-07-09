import os
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class AgenteEmail:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.email_from = "shadow4stories@gmail.com"
        self.password = os.getenv("GMAIL_APP_PASSWORD", "aissarah")

    def ejecutar(self):
        resultados = {}

        leads = self._cargar_o_generar_leads()
        if not leads:
            return json.dumps({"status": "sin_leads"})

        resultados["email_config"] = self._verificar_smtp()

        if resultados["email_config"].get("smtp_ok"):
            resultados["enviados"] = self._enviar_correos(leads)
        else:
            resultados["enviados"] = self._guardar_para_enviar(leads)

        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _verificar_smtp(self):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.email_from, self.password)
            server.quit()
            return {"smtp_ok": True, "email": self.email_from}
        except smtplib.SMTPAuthenticationError:
            print("[EMAIL] Error de autenticacion Gmail.")
            print("[EMAIL] NECESITAS: Ir a https://myaccount.google.com/security y crear una 'Contrasena de aplicacion'")
            print("[EMAIL] O activar 'Acceso de apps menos seguras'")
            return {"smtp_ok": False, "error": "autenticacion", "solucion": "Crear contrasena de aplicacion en Google"}
        except Exception as e:
            return {"smtp_ok": False, "error": str(e)}

    def _cargar_o_generar_leads(self):
        leads = []
        try:
            with open("data/leads.json", "r", encoding="utf-8") as f:
                leads = json.load(f)
        except:
            pass

        if not leads:
            for ciudad in ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao"][:3]:
                lead = self.ia.extract_json(
                    "Eres un generador de leads B2B realista para Espana.",
                    f"Genera un lead en {ciudad} que necesite automatizacion/IA. "
                    f"JSON con: 'empresa', 'sector', 'necesidad', 'email' (inventado)"
                )
                if lead and lead.get("empresa"):
                    leads.append(lead)
            if leads:
                with open("data/leads.json", "w", encoding="utf-8") as f:
                    json.dump(leads, f, indent=2, ensure_ascii=False)

        return leads

    def _enviar_correos(self, leads):
        enviados = []
        for lead in leads[:5]:
            try:
                empresa = lead.get("empresa", "Cliente")
                necesidad = lead.get("necesidad", "automatizar procesos")
                email_to = lead.get("email", f"info@{empresa.lower().replace(' ','')}.es")

                asunto = f"Transforma {empresa} con Automatizacion e IA"
                cuerpo = self.ia.think(
                    "Eres un vendedor B2B experto. Escribes correos que abren y responden.",
                    f"Escribe email de venta para {empresa}. Necesidad: {necesidad}\n\n"
                    f"Asunto atractivo, saludo personalizado, ofrecemos automatizacion e IA, "
                    f"caso de exito breve, PRIMERA CONSULTORIA GRATIS, CTA agendar llamada. "
                    f"Firma: Shadow Tech | Automatizacion con IA"
                )

                msg = MIMEMultipart()
                msg["From"] = self.email_from
                msg["To"] = email_to
                msg["Subject"] = asunto
                msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(self.email_from, self.password)
                server.send_message(msg)
                server.quit()

                enviados.append({"empresa": empresa, "email": email_to, "status": "enviado"})
                print(f"[EMAIL] Enviado a {empresa} <{email_to}>")
                time.sleep(3)
            except Exception as e:
                enviados.append({"empresa": lead.get("empresa", ""), "error": str(e)})
            time.sleep(2)

        return enviados

    def _guardar_para_enviar(self, leads):
        guardados = []
        for lead in leads[:5]:
            empresa = lead.get("empresa", "Cliente")
            email_to = lead.get("email", f"info@{empresa.lower().replace(' ','')}.es")
            necesidad = lead.get("necesidad", "automatizar")
            guardados.append({
                "empresa": empresa,
                "email": email_to,
                "necesidad": necesidad,
                "pendiente": True
            })

        with open("data/emails_pendientes.json", "w", encoding="utf-8") as f:
            json.dump(guardados, f, indent=2, ensure_ascii=False)

        print(f"[EMAIL] {len(guardados)} correos guardados como pendientes. Revisa data/emails_pendientes.json")
        return guardados