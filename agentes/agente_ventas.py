import os
import json
import requests
import base64
from datetime import datetime

class AgenteVentas:
    def __init__(self, ia, mode):
        self.ia = ia
        self.mode = mode
        self.paypal_id = os.getenv("PAYPAL_CLIENT_ID", "")
        self.paypal_secret = os.getenv("PAYPAL_CLIENT_SECRET", "")

    def ejecutar(self):
        resultados = {}
        resultados["paypal_token"] = self._obtener_token_paypal()
        resultados["ventas"] = self._procesar_ventas()
        resultados["facturas"] = self._generar_facturas()
        return json.dumps(resultados, indent=2, ensure_ascii=False)

    def _obtener_token_paypal(self):
        if not self.paypal_id or not self.paypal_secret:
            return {"status": "no_configurado"}
        try:
            url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
            auth = base64.b64encode(f"{self.paypal_id}:{self.paypal_secret}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}", "Accept": "application/json"}
            data = {"grant_type": "client_credentials"}
            resp = requests.post(url, headers=headers, data=data, timeout=15)
            if resp.status_code == 200:
                return {"status": "ok", "token": "obtenido"}
            return {"error": resp.text[:200]}
        except Exception as e:
            return {"error": str(e)}

    def _procesar_ventas(self):
        leads_file = "data/leads.json"
        if not os.path.exists(leads_file):
            return {"vendido": False, "mensaje": "sin_leads"}
        with open(leads_file, "r") as f:
            leads = json.load(f)

        for lead in leads[:2]:
            empresa = lead.get("empresa", "Cliente")
            necesidad = lead.get("necesidad", "automatizacion")

            plan = self.ia.extract_json(
                "Eres un vendedor B2B que cierra ventas por $500-5000.",
                f"Cierra venta para {empresa} ({necesidad}). "
                f"Genera: {{'paquete':'basico/pro/premium','precio_usd':500-3000,"
                f"'descripcion':'que incluye','enlace_pago':'pendiente_paypal'}}"
            )
            if plan and plan.get("precio_usd"):
                try:
                    url = "https://api-m.sandbox.paypal.com/v1/payments/payment"
                    auth = base64.b64encode(f"{self.paypal_id}:{self.paypal_secret}".encode()).decode()
                    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
                    payment = {
                        "intent": "sale",
                        "payer": {"payment_method": "paypal"},
                        "transactions": [{"amount": {"total": str(plan["precio_usd"]), "currency": "USD"},
                                          "description": plan.get("descripcion", "Servicios Shadow Tech")}],
                        "redirect_urls": {"return_url": "https://shadowtech.com/success", "cancel_url": "https://shadowtech.com/cancel"}
                    }
                    resp = requests.post(url, headers=headers, json=payment, timeout=15)
                    if resp.status_code == 201:
                        data = resp.json()
                        for link in data.get("links", []):
                            if link["rel"] == "approval_url":
                                plan["enlace_pago"] = link["href"]
                                break
                    lead["plan"] = plan
                    lead["estado"] = "oferta_enviada"
                except:
                    lead["plan"] = plan
                    lead["estado"] = "oferta_generada"

        with open(leads_file, "w") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        return {"procesados": len(leads)}

    def _generar_facturas(self):
        leads_file = "data/leads.json"
        if not os.path.exists(leads_file):
            return []
        with open(leads_file, "r") as f:
            leads = json.load(f)
        facturas = []
        for lead in leads:
            if "venta" in lead.get("estado", ""):
                factura = self.ia.think(
                    "Eres un sistema de facturacion.",
                    f"Genera factura para {lead.get('empresa')} por {lead.get('plan',{}).get('precio_usd','500')} USD."
                )
                facturas.append({"empresa": lead.get("empresa"), "factura": factura[:200]})
        return facturas