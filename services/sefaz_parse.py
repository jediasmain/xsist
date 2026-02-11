from __future__ import annotations

import base64
import gzip
import html
from lxml import etree


def _safe_parse(xml_text: str):
    s = (xml_text or "").strip()

    # Se veio escapado (&lt;...&gt;), desescapa
    if s and not s.startswith("<") and "&lt;" in s:
        s = html.unescape(s).strip()

    return etree.fromstring(s.encode("utf-8"))


def extract_ret_xml_from_soap(soap_xml: str) -> str:
    """
    Dentro do SOAP geralmente vem um nó ...Result com o XML do retDistDFeInt.
    """
    root = _safe_parse(soap_xml)

    # Procura qualquer nó que tenha "Result" no nome
    result_nodes = root.xpath("//*[contains(local-name(), 'Result')]")
    for n in result_nodes:
        if n.text and n.text.strip():
            return n.text.strip()

    # Fallback: tenta achar retDistDFeInt direto
    ret_nodes = root.xpath("//*[local-name()='retDistDFeInt']")
    if ret_nodes:
        return etree.tostring(ret_nodes[0], encoding="utf-8").decode("utf-8")

    raise RuntimeError("Não encontrei Result/retDistDFeInt dentro do SOAP.")


def _decode_doczip(doczip_text: str) -> str:
    data = base64.b64decode(doczip_text)
    xml_bytes = gzip.decompress(data)
    return xml_bytes.decode("utf-8", errors="replace")


def parse_ret_distdfeint(ret_xml: str) -> dict:
    """
    Lê o retDistDFeInt e devolve cStat, xMotivo e docs (docZip decodificado).
    """
    ret_root = _safe_parse(ret_xml)

    cstat = ret_root.xpath("string(//*[local-name()='cStat'])").strip()
    xmotivo = ret_root.xpath("string(//*[local-name()='xMotivo'])").strip()

    docs = []
    for dz in ret_root.xpath("//*[local-name()='docZip']"):
        schema = dz.get("schema", "")
        nsu = dz.get("NSU", "") or dz.get("nsu", "")
        xml = _decode_doczip(dz.text or "")
        docs.append({"nsu": nsu, "schema": schema, "xml": xml})

    return {"cStat": cstat, "xMotivo": xmotivo, "docs": docs}