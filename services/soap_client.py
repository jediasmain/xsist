from __future__ import annotations

import requests

SOAP_ENV_NS = "http://schemas.xmlsoap.org/soap/envelope/"


def wrap_soap(body_xml: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="{SOAP_ENV_NS}">
  <soap:Body>
    {body_xml}
  </soap:Body>
</soap:Envelope>"""


def post_soap(url: str, soap_action: str, envelope_xml: str, cert: tuple[str, str] | None = None) -> requests.Response:
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": soap_action,
        "User-Agent": "XSist/1.0",
    }
    return requests.post(url, data=envelope_xml.encode("utf-8"), headers=headers, cert=cert, timeout=30)