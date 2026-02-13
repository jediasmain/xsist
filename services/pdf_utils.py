from __future__ import annotations

from fpdf import FPDF
from lxml import etree


def _xpath_str(root, expr: str) -> str:
    try:
        return (root.xpath(expr) or "").strip()
    except Exception:
        return ""


def _sanitize(text: str) -> str:
    text = (text or "").replace("\r", " ").replace("\t", " ").strip()
    # remove caracteres de controle
    text = "".join(ch for ch in text if ch == "\n" or ord(ch) >= 32)
    return text or "-"


def _wrap_no_space(text: str, width: int = 28) -> str:
    """
    Quebra strings longas sem espaços (ex.: chave) em linhas menores.
    """
    text = (text or "").strip()
    if not text:
        return "-"
    return "\n".join(text[i : i + width] for i in range(0, len(text), width))


def extract_basic_fields(xml_text: str) -> dict:
    root = etree.fromstring(xml_text.encode("utf-8", errors="ignore"))

    xml_lower = xml_text.lower()
    tipo = "DESCONHECIDO"
    if "infnfe" in xml_lower:
        tipo = "NFE"
    elif "infcte" in xml_lower:
        tipo = "CTE"

    chave = _xpath_str(root, "string(//*[local-name()='infNFe']/@Id)")
    if chave.startswith("NFe") and len(chave) >= 47:
        chave = chave[3:47]
    else:
        chave2 = _xpath_str(root, "string(//*[local-name()='infCte' or local-name()='infCTe']/@Id)")
        if chave2.startswith("CTe") and len(chave2) >= 47:
            chave = chave2[3:47]
        else:
            chnfe = _xpath_str(root, "string(//*[local-name()='chNFe'])")
            if len(chnfe) == 44 and chnfe.isdigit():
                chave = chnfe
            chcte = _xpath_str(root, "string(//*[local-name()='chCTe'])")
            if len(chcte) == 44 and chcte.isdigit():
                chave = chcte

    emit = _xpath_str(root, "string(//*[local-name()='emit']/*[local-name()='xNome'])")
    dest = _xpath_str(root, "string(//*[local-name()='dest']/*[local-name()='xNome'])")

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

    # largura útil fixa (não depende do X atual)
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", size=14)
    pdf.set_x(pdf.l_margin)
    pdf.cell(usable_w, 10, "XSist - Resumo do XML", ln=True)

    pdf.set_font("Helvetica", size=11)
    pdf.ln(2)

    def line(label: str, value: str):
        value = _sanitize(value)

        if label.lower() in ("chave", "qrcode", "url"):
            value = _wrap_no_space(value, 28)

        pdf.set_x(pdf.l_margin)  # garante margem esquerda
        pdf.multi_cell(usable_w, 7, f"{label}: {value}")

    line("Tipo", fields["tipo"])
    line("Chave", fields["chave"])
    line("Emitente", fields["emitente"])
    line("Destinatário", fields["destinatario"])
    line("Data", fields["data"])
    line("Valor", fields["valor"])

    return bytes(pdf.output(dest="S"))