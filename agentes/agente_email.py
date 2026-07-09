import os
import json
import smtplib
import imaplib
import email
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class AgenteEmail:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.email_from = "shadow4stories@gmail.com"
        self.password = os.getenv("GMAIL_APP_PASSWORD", "")
        self.leads_file = "data/leads.json"
        self.respuestas_pendientes = "data/respuestas_pendientes.json"

    def ejecutar(self):
        resultados = {}
        resultados["enviar_propuestas"] = self._enviar_a_leads()
        resultados["responder_recibidos"] = self._revisar_y_responder()
        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _enviar_a_leads(self):
        leads = self._cargar_leads()
        if not leads:
            return self._generar_y_guardar_leads()
        enviados = 0
        for lead in leads[:3]:
            try:
                empresa = lead.get("empresa", "Cliente")
                email_to = lead.get("email", f"info@{empresa.lower().replace(' ','')}.es")
                necesidad = lead.get("necesidad", "automatizar")

                asunto = f"Transforma {empresa} con Automatizacion e IA - Shadow Tech"
                cuerpo = self.ia.think(
                    "Eres un vendedor B2B experto en Espana.",
                    f"Escribe email de venta para {empresa}. Necesidad: {necesidad}\n\n"
                    f"Asunto atractivo, saludo, ofrecemos automatizacion e IA, "
                    f"PRIMERA CONSULTORIA GRATIS, CTA: responder este correo. "
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
                enviados += 1
                lead["enviado"] = True
                lead["fecha_envio"] = str(datetime.now())
                time.sleep(2)
            except Exception as e:
                print(f"[EMAIL] Error enviando a {empresa}: {e}")
        with open(self.leads_file, "w") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        return {"enviados": enviados, "total_leads": len(leads)}

    def _revisar_y_responder(self):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.email_from, self.password)
            mail.select("inbox")
            status, mensajes = mail.search(None, "UNSEEN")
            respondidos = 0
            if status == "OK":
                for num in mensajes[0].split()[:5]:
                    status, data = mail.fetch(num, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    remitente = msg["From"]
                    asunto = msg["Subject"]
                    cuerpo = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                cuerpo = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        cuerpo = msg.get_payload(decode=True).decode(errors="ignore")

                    respuesta = self.ia.think(
                        "Eres un vendedor experto respondiendo correos de clientes interesados. Debes convertir la conversacion en venta.",
                        f"Cliente: {remitente}\nAsunto: {asunto}\nMensaje: {cuerpo[:500]}\n\n"
                        f"Responde agradeciendo, resolviendo dudas, y ofreciendo agendar llamada. Ofrece PRIMERA CONSULTORIA GRATIS. Firma: Shadow Tech."
                    )
                    reply_msg = MIMEMultipart()
                    reply_msg["From"] = self.email_from
                    reply_msg["To"] = remitente
                    reply_msg["Subject"] = f"Re: {asunto}"
                    reply_msg.attach(MIMEText(respuesta, "plain", "utf-8"))

                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(self.email_from, self.password)
                    server.send_message(reply_msg)
                    server.quit()
                    respondidos += 1
                    time.sleep(2)

                    mail.store(num, "+FLAGS", "\\Answered")

            mail.logout()
            return {"respondidos": respondidos}
        except Exception as e:
            return {"error_imap": str(e)}

    def _cargar_leads(self):
        if os.path.exists(self.leads_file):
            with open(self.leads_file, "r") as f:
                return json.load(f)
        return []

    def _generar_y_guardar_leads(self):
        leads = []
        for ciudad in ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Malaga"][:4]:
            lead = self.ia.extract_json(
                "Genera leads B2B realistas para Espana.",
                f"Lead en {ciudad} que necesite automatizacion/IA. JSON: 'empresa','sector','necesidad','email'"
            )
            if lead and lead.get("empresa"):
                lead["enviado"] = False
                leads.append(lead)
        with open(self.leads_file, "w") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        return {"leads_generados": len(leads)}