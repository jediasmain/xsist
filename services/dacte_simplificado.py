from __future__ import annotations

from io import BytesIO
from typing import Any

import qrcode
from fpdf import FPDF
from lxml import etree


def _s(x: Any) -> str:
    return (str(x) if x is not None else "").strip()


def _xpath_str(node, expr: str) -> str:
    try:
        return _s(node.xpath(f"string({expr})"))
    except Exception:
        return ""


def _detect_chave_cte(root, xml_text: str) -> str:
    # 1) Id="CTe<44>"
    id_attr = _xpath_str(root, "//*[local-name()='infCte' or local-name()='infCTe']/@Id")
    if id_attr.startswith("CTe") and len(id_attr) >= 47:
        return id_attr[3:47]

    # 2) chCTe
    chcte = _xpath_str(root, "//*[local-name()='chCTe']")
    if len(chcte) == 44 and chcte.isdigit():
        return chcte

    # 3) fallback: procurar 44 dígitos depois de "CTe"
    i = xml_text.find("CTe")
    if i != -1:
        cand = "".join(c for c in xml_text[i:i+60] if c.isdigit())
        if len(cand) >= 44:
            return cand[:44]

    return ""


def extract_cte_for_dacte(xml_text: str) -> dict:
    root = etree.fromstring(xml_text.encode("utf-8", errors="ignore"))

    chave = _detect_chave_cte(root, xml_text)

    # ide
    nCT = _xpath_str(root, "//*[local-name()='ide']/*[local-name()='nCT']")
    serie = _xpath_str(root, "//*[local-name()='ide']/*[local-name()='serie']")
    dhEmi = (
        _xpath_str(root, "//*[local-name()='ide']/*[local-name()='dhEmi']")
        or _xpath_str(root, "//*[local-name()='ide']/*[local-name()='dEmi']")
    )
    natOp = _xpath_str(root, "//*[local-name()='ide']/*[local-name()='natOp']")
    mod = _xpath_str(root, "//*[local-name()='ide']/*[local-name()='mod']")
    tpCTe = _xpath_str(root, "//*[local-name()='ide']/*[local-name()='tpCTe']")

    # participantes
    emit_nome = _xpath_str(root, "//*[local-name()='emit']/*[local-name()='xNome']")
    emit_cnpj = _xpath_str(root, "//*[local-name()='emit']/*[local-name()='CNPJ']")

    rem_nome = _xpath_str(root, "//*[local-name()='rem']/*[local-name()='xNome']")
    rem_doc = (
        _xpath_str(root, "//*[local-name()='rem']/*[local-name()='CNPJ']")
        or _xpath_str(root, "//*[local-name()='rem']/*[local-name()='CPF']")
    )

    dest_nome = _xpath_str(root, "//*[local-name()='dest']/*[local-name()='xNome']")
    dest_doc = (
        _xpath_str(root, "//*[local-name()='dest']/*[local-name()='CNPJ']")
        or _xpath_str(root, "//*[local-name()='dest']/*[local-name()='CPF']")
    )

    # valores
    vTPrest = _xpath_str(root, "//*[local-name()='vPrest']/*[local-name()='vTPrest']")
    vRec = _xpath_str(root, "//*[local-name()='vPrest']/*[local-name()='vRec']")

    # carga (quando existir)
    vCarga = _xpath_str(root, "//*[local-name()='infCarga']/*[local-name()='vCarga']")
    proPred = _xpath_str(root, "//*[local-name()='infCarga']/*[local-name()='proPred']")
    xOutCat = _xpath_str(root, "//*[local-name()='infCarga']/*[local-name()='xOutCat']")

    # componentes do valor (Comp)
    comps = []
    comp_nodes = root.xpath("//*[local-name()='vPrest']/*[local-name()='Comp']")
    for c in comp_nodes:
        xNome = _xpath_str(c, ".//*[local-name()='xNome']")
        vComp = _xpath_str(c, ".//*[local-name()='vComp']")
        comps.append({"xNome": xNome, "vComp": vComp})

    # QRCode (CT-e)
    qr = (
        _xpath_str(root, "//*[local-name()='qrCodCTe']")
        or _xpath_str(root, "//*[local-name()='qrCode']")
        or chave
    )
    if not qr:
        qr = chave

    return {
        "chave": chave,
        "nCT": nCT,
        "serie": serie,
        "dhEmi": dhEmi,
        "natOp": natOp,
        "mod": mod,
        "tpCTe": tpCTe,
        "emit_nome": emit_nome,
        "emit_cnpj": emit_cnpj,
        "rem_nome": rem_nome,
        "rem_doc": rem_doc,
        "dest_nome": dest_nome,
        "dest_doc": dest_doc,
        "vTPrest": vTPrest,
        "vRec": vRec,
        "vCarga": vCarga,
        "proPred": proPred,
        "xOutCat": xOutCat,
        "qr": qr,
        "comps": comps,
    }


def _qr_png_bytes(text: str) -> bytes:
    img = qrcode.make(text or " ")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def cte_xml_to_dacte_pdf_bytes(xml_text: str) -> bytes:
    d = extract_cte_for_dacte(xml_text)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 8, "DACTE SIMPLIFICADO (CT-e)", ln=True)

    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"Chave: {d['chave'] or '-'}")
    pdf.multi_cell(0, 6, f"CT-e: {d['nCT'] or '-'}   Série: {d['serie'] or '-'}   Emissão: {d['dhEmi'] or '-'}")
    pdf.multi_cell(0, 6, f"Natureza: {d['natOp'] or '-'}   Mod: {d['mod'] or '-'}   tpCTe: {d['tpCTe'] or '-'}")

    # QR no canto direito
    try:
        qr_bytes = _qr_png_bytes(d["qr"])
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(qr_bytes)
        tmp.close()
        pdf.image(tmp.name, x=165, y=10, w=35, h=35)
        os.unlink(tmp.name)
    except Exception:
        pass

    pdf.ln(2)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Emitente", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"{d['emit_nome'] or '-'}  |  CNPJ: {d['emit_cnpj'] or '-'}")

    pdf.ln(1)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Remetente", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"{d['rem_nome'] or '-'}  |  Doc: {d['rem_doc'] or '-'}")

    pdf.ln(1)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Destinatário", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"{d['dest_nome'] or '-'}  |  Doc: {d['dest_doc'] or '-'}")

    pdf.ln(2)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Valores", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"V. Total Prestação: {d['vTPrest'] or '-'}   V. a Receber: {d['vRec'] or '-'}")

    if d["comps"]:
        pdf.ln(1)
        pdf.set_font("Helvetica", size=10)
        pdf.cell(120, 6, "Componente", border=1)
        pdf.cell(60, 6, "Valor", border=1, ln=True)
        for c in d["comps"][:25]:
            pdf.cell(120, 6, _s(c["xNome"])[:60], border=1)
            pdf.cell(60, 6, _s(c["vComp"])[:20], border=1, ln=True)

    pdf.ln(2)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Carga (se informado)", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(
        0, 6,
        f"V. Carga: {d['vCarga'] or '-'}   Produto Pred.: {d['proPred'] or '-'}   Out. Cat.: {d['xOutCat'] or '-'}"
    )

    return bytes(pdf.output(dest="S"))