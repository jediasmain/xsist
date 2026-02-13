from __future__ import annotations

from fpdf import FPDF
from lxml import etree


def _xpath_str(root, expr: str) -> str:
    try:
        return (root.xpath(expr) or "").strip()
    except Exception:
        return ""


def extract_basic_fields(xml_text: str) -> dict:
    """
    Extrai alguns campos básicos de NF-e ou CT-e (de forma tolerante).
    Não garante padrão SEFAZ, é só para um PDF-resumo.
    """
    root = etree.fromstring(xml_text.encode("utf-8", errors="ignore"))

    # tenta descobrir tipo
    xml_lower = xml_text.lower()
    tipo = "DESCONHECIDO"
    if "infnfe" in xml_lower:
        tipo = "NFE"
    elif "infcte" in xml_lower:
        tipo = "CTE"

    # chave (Id="NFe...." / "CTe....")
    chave = _xpath_str(root, "string(//*[local-name()='infNFe']/@Id)")
    if chave.startswith("NFe"):
        chave = chave[3:47]
    else:
        chave2 = _xpath_str(root, "string(//*[local-name()='infCte' or local-name()='infCTe']/@Id)")
        if chave2.startswith("CTe"):
            chave = chave2[3:47]
        else:
            # fallback: chNFe/chCTe
            chnfe = _xpath_str(root, "string(//*[local-name()='chNFe'])")
            if len(chnfe) == 44:
                chave = chnfe
            chcte = _xpath_str(root, "string(//*[local-name()='chCTe'])")
            if len(chcte) == 44:
                chave = chcte

    # campos comuns
    emit = _xpath_str(root, "string(//*[local-name()='emit']/*[local-name()='xNome'])")
    dest = _xpath_str(root, "string(//*[local-name()='dest']/*[local-name()='xNome'])")

    # data (varia)
    dh = (
        _xpath_str(root, "string(//*[local-name()='ide']/*[local-name()='dhEmi'])")
        or _xpath_str(root, "string(//*[local-name()='ide']/*[local-name()='dEmi'])")
        or _xpath_str(root, "string(//*[local-name()='ide']/*[local-name()='dhCont'])")
    )

    valor = ""
    if tipo == "NFE":
        valor = _xpath_str(root, "string(//*[local-name()='ICMSTot']/*[local-name()='vNF'])")
    elif tipo == "CTE":
        valor = _xpath_str(root, "string(//*[local-name()='vPrest']/*[local-name()='vTPrest'])")

    return {
        "tipo": tipo,
        "chave": chave,
        "emitente": emit,
        "destinatario": dest,
        "data": dh,
        "valor": valor,
    }


def xml_to_pdf_bytes(xml_text: str) -> bytes:
    fields = extract_basic_fields(xml_text)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, "XSist - Resumo do XML", ln=True)

    pdf.set_font("Helvetica", size=11)
    pdf.ln(2)

    def line(label: str, value: str):
        value = value or "-"
        pdf.multi_cell(0, 7, f"{label}: {value}")

    line("Tipo", fields["tipo"])
    line("Chave", fields["chave"])
    line("Emitente", fields["emitente"])
    line("Destinatário", fields["destinatario"])
    line("Data", fields["data"])
    line("Valor", fields["valor"])

    return bytes(pdf.output(dest="S"))