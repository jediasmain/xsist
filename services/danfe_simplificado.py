from __future__ import annotations

from io import BytesIO
from typing import Any

import qrcode
from fpdf import FPDF
from lxml import etree


def _s(x: Any) -> str:
    """string segura"""
    return (str(x) if x is not None else "").strip()


def _xpath(root, expr: str) -> str:
    try:
        return _s(root.xpath(expr))
    except Exception:
        return ""


def _xpath_str(root, expr: str) -> str:
    try:
        return _s(root.xpath(f"string({expr})"))
    except Exception:
        return ""


def extract_nfe_for_danfe(xml_text: str) -> dict:
    root = etree.fromstring(xml_text.encode("utf-8", errors="ignore"))

    # chave
    id_attr = _xpath_str(root, "//*[local-name()='infNFe']/@Id")
    chave = id_attr[3:47] if id_attr.startswith("NFe") else ""

    # emitente/destinatário
    emit_nome = _xpath_str(root, "//*[local-name()='emit']/*[local-name()='xNome']")
    emit_cnpj = _xpath_str(root, "//*[local-name()='emit']/*[local-name()='CNPJ']")
    dest_nome = _xpath_str(root, "//*[local-name()='dest']/*[local-name()='xNome']")
    dest_doc = (
        _xpath_str(root, "//*[local-name()='dest']/*[local-name()='CNPJ']")
        or _xpath_str(root, "//*[local-name()='dest']/*[local-name()='CPF']")
    )

    # ide
    nNF = _xpath_str(root, "//*[local-name()='ide']/*[local-name()='nNF']")
    serie = _xpath_str(root, "//*[local-name()='ide']/*[local-name()='serie']")
    dhEmi = (
        _xpath_str(root, "//*[local-name()='ide']/*[local-name()='dhEmi']")
        or _xpath_str(root, "//*[local-name()='ide']/*[local-name()='dEmi']")
    )

    # totais
    vNF = _xpath_str(root, "//*[local-name()='ICMSTot']/*[local-name()='vNF']")
    vProd = _xpath_str(root, "//*[local-name()='ICMSTot']/*[local-name()='vProd']")
    vICMS = _xpath_str(root, "//*[local-name()='ICMSTot']/*[local-name()='vICMS']")

    # QR (às vezes existe no XML)
    qr = _xpath_str(root, "//*[local-name()='qrCode']")
    if not qr:
        # fallback: pelo menos usa a chave como texto do QR
        qr = chave

    # itens
    itens = []
    det_nodes = root.xpath("//*[local-name()='det']")
    for det in det_nodes:
        nItem = det.get("nItem", "")
        cProd = _xpath_str(det, ".//*[local-name()='prod']/*[local-name()='cProd']")
        xProd = _xpath_str(det, ".//*[local-name()='prod']/*[local-name()='xProd']")
        qCom = _xpath_str(det, ".//*[local-name()='prod']/*[local-name()='qCom']")
        uCom = _xpath_str(det, ".//*[local-name()='prod']/*[local-name()='uCom']")
        vUnCom = _xpath_str(det, ".//*[local-name()='prod']/*[local-name()='vUnCom']")
        vProdItem = _xpath_str(det, ".//*[local-name()='prod']/*[local-name()='vProd']")

        itens.append(
            {
                "nItem": nItem,
                "cProd": cProd,
                "xProd": xProd,
                "qCom": qCom,
                "uCom": uCom,
                "vUnCom": vUnCom,
                "vProd": vProdItem,
            }
        )

    return {
        "chave": chave,
        "emit_nome": emit_nome,
        "emit_cnpj": emit_cnpj,
        "dest_nome": dest_nome,
        "dest_doc": dest_doc,
        "nNF": nNF,
        "serie": serie,
        "dhEmi": dhEmi,
        "vNF": vNF,
        "vProd": vProd,
        "vICMS": vICMS,
        "qr": qr,
        "itens": itens,
    }


def _qr_png_bytes(text: str) -> bytes:
    img = qrcode.make(text or " ")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def nfe_xml_to_danfe_pdf_bytes(xml_text: str) -> bytes:
    d = extract_nfe_for_danfe(xml_text)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 8, "DANFE SIMPLIFICADO (NF-e)", ln=True)

    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"Chave: {d['chave'] or '-'}")
    pdf.multi_cell(0, 6, f"NF: {d['nNF'] or '-'}   Série: {d['serie'] or '-'}   Emissão: {d['dhEmi'] or '-'}")

    pdf.ln(2)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Emitente", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"{d['emit_nome'] or '-'}  |  CNPJ: {d['emit_cnpj'] or '-'}")

    pdf.ln(1)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Destinatário", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"{d['dest_nome'] or '-'}  |  Doc: {d['dest_doc'] or '-'}")

    # QR code (canto direito)
    try:
        qr_bytes = _qr_png_bytes(d["qr"])
        # fpdf2 aceita arquivo; vamos usar temporário em memória via BytesIO -> precisa nome
        # solução simples: cria arquivo temporário
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(qr_bytes)
        tmp.close()
        pdf.image(tmp.name, x=165, y=10, w=35, h=35)
        os.unlink(tmp.name)
    except Exception:
        pass

    pdf.ln(3)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Itens", ln=True)

    # Cabeçalho tabela
    pdf.set_font("Helvetica", size=9)
    pdf.cell(10, 6, "Item", border=1)
    pdf.cell(25, 6, "Codigo", border=1)
    pdf.cell(90, 6, "Descricao", border=1)
    pdf.cell(20, 6, "Qtd", border=1)
    pdf.cell(20, 6, "V.Unit", border=1)
    pdf.cell(25, 6, "V.Prod", border=1, ln=True)

    # Linhas
    for it in d["itens"][:40]:  # limita para não estourar (MVP)
        pdf.cell(10, 6, _s(it["nItem"]), border=1)
        pdf.cell(25, 6, _s(it["cProd"])[:12], border=1)
        pdf.cell(90, 6, _s(it["xProd"])[:45], border=1)
        qtd = f"{_s(it['qCom'])} {_s(it['uCom'])}".strip()
        pdf.cell(20, 6, qtd[:12], border=1)
        pdf.cell(20, 6, _s(it["vUnCom"])[:12], border=1)
        pdf.cell(25, 6, _s(it["vProd"])[:12], border=1, ln=True)

    pdf.ln(2)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, "Totais", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, f"V.Produtos: {d['vProd'] or '-'}   ICMS: {d['vICMS'] or '-'}   V.NF: {d['vNF'] or '-'}")

    return bytes(pdf.output(dest="S"))