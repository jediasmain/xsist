from __future__ import annotations

from lxml import etree


def extract_key_and_type(xml_text: str) -> tuple[str | None, str | None]:
    """
    Tenta descobrir:
    - tipo: 'NFE' ou 'CTE'
    - chave: 44 dígitos

    Retorna (chave, tipo). Se não achar, retorna (None, None) ou (None, tipo).
    """
    try:
        root = etree.fromstring(xml_text.encode("utf-8"))
    except Exception:
        return None, None

    # 1) Tenta pegar pela tag infNFe / infCte (Id="NFe<CHAVE>" ou Id="CTe<CHAVE>")
    inf_nfe = root.xpath("//*[local-name()='infNFe']")
    if inf_nfe:
        id_attr = inf_nfe[0].get("Id", "")
        if id_attr.startswith("NFe") and len(id_attr) >= 47:
            return id_attr[3:47], "NFE"

    inf_cte = root.xpath("//*[local-name()='infCte' or local-name()='infCTe']")
    if inf_cte:
        id_attr = inf_cte[0].get("Id", "")
        if id_attr.startswith("CTe") and len(id_attr) >= 47:
            return id_attr[3:47], "CTE"

    # 2) Fallback: tenta achar chNFe / chCTe em qualquer lugar do XML
    chnfe = root.xpath("string(//*[local-name()='chNFe'])").strip()
    if len(chnfe) == 44 and chnfe.isdigit():
        return chnfe, "NFE"

    chcte = root.xpath("string(//*[local-name()='chCTe' or local-name()='chCTe'])").strip()
    if len(chcte) == 44 and chcte.isdigit():
        return chcte, "CTE"

    # Se não achou chave, pelo menos tenta inferir tipo pelo nome das tags
    xml_lower = xml_text.lower()
    if "infnfe" in xml_lower:
        return None, "NFE"
    if "infcte" in xml_lower or "infcte" in xml_lower:
        return None, "CTE"

    return None, None