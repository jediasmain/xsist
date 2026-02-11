from __future__ import annotations

def only_digits(s: str) -> str:
    return "".join(c for c in (s or "") if c.isdigit())

def build_distdfeint_cons_chave(chave: str, cnpj: str, tp_amb: int = 1) -> str:
    """
    Monta o XML oficial do pedido: distDFeInt (consulta por chave).
    tp_amb: 1=Produção, 2=Homologação
    """
    ch = only_digits(chave)
    cnpj = only_digits(cnpj)

    if len(ch) != 44:
        raise ValueError("Chave deve ter 44 dígitos.")
    if len(cnpj) != 14:
        raise ValueError("CNPJ deve ter 14 dígitos.")

    cuf_autor = ch[:2]  # primeiro campo da chave = cUF

    return f"""<?xml version="1.0" encoding="utf-8"?>
<distDFeInt xmlns="http://www.portalfiscal.inf.br/nfe" versao="1.01">
  <tpAmb>{tp_amb}</tpAmb>
  <cUFAutor>{cuf_autor}</cUFAutor>
  <CNPJ>{cnpj}</CNPJ>
  <consChNFe>
    <chNFe>{ch}</chNFe>
  </consChNFe>
</distDFeInt>"""