from __future__ import annotations

from services.cert_utils import pfx_to_pem_files
from services.sefaz_payloads import build_distdfeint_cons_chave
from services.soap_client import wrap_soap, post_soap
from services.sefaz_parse import extract_ret_xml_from_soap, parse_ret_distdfeint


# Endpoint do serviço (produção). Pode mudar com o tempo; ajustamos se necessário.
NFE_DIST_URL = "https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx"

# SOAPAction típico
SOAP_ACTION = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe/nfeDistDFeInteresse"


def _only_digits(s: str) -> str:
    return "".join(c for c in (s or "") if c.isdigit())


def download_nfe_xml_by_key_official(
    *,
    chave: str,
    pfx_path: str | None,
    pfx_password: str | None,
    cnpj: str | None,
    tp_amb: int = 1,
) -> tuple[bool, str | None, str]:
    """
    NF-e Distribuição DF-e (consulta por chave).
    Retorna (ok, xml_text, msg).
    """
    chave = _only_digits(chave)
    cnpj = _only_digits(cnpj or "")

    if len(chave) != 44:
        return False, None, "Chave inválida (precisa 44 dígitos)."

    if not pfx_path or not pfx_password:
        return False, None, "Falta configurar certificado A1 no conector (pfx_path/senha)."

    if len(cnpj) != 14:
        return False, None, "Falta informar CNPJ (14 dígitos) do certificado no conector."

    # 1) monta XML do pedido distDFeInt
    dist_xml = build_distdfeint_cons_chave(chave=chave, cnpj=cnpj, tp_amb=int(tp_amb))

    # 2) corpo SOAP (operação nfeDistDFeInteresse)
    body = f"""
<nfeDistDFeInteresse xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe">
  <nfeDadosMsg><![CDATA[{dist_xml}]]></nfeDadosMsg>
</nfeDistDFeInteresse>
""".strip()

    envelope = wrap_soap(body)

    # 3) certificado mTLS: PFX -> PEM temporário
    cert_pem, key_pem = pfx_to_pem_files(pfx_path, pfx_password)

    # 4) POST SOAP
    try:
        resp = post_soap(
            url=NFE_DIST_URL,
            soap_action=SOAP_ACTION,
            envelope_xml=envelope,
            cert=(cert_pem, key_pem),
        )
    except Exception as e:
        return False, None, f"Falha HTTP/Conexão com SEFAZ: {e}"

    if resp.status_code != 200:
        # corta texto para não explodir
        return False, None, f"HTTP {resp.status_code}: {resp.text[:400]}"

    # 5) parse SOAP -> retDistDFeInt -> docZip -> xml
    try:
        ret_xml = extract_ret_xml_from_soap(resp.text)
        parsed = parse_ret_distdfeint(ret_xml)
    except Exception as e:
        return False, None, f"HTTP 200 mas falhou ao parsear retorno: {e}"

    cstat = parsed.get("cStat", "")
    xmotivo = parsed.get("xMotivo", "")
    docs = parsed.get("docs", [])

    # 138 = Documentos localizados
    # 137 = Nenhum documento localizado
    if cstat != "138":
        return False, None, f"SEFAZ cStat={cstat} | {xmotivo}"

    if not docs:
        return False, None, "SEFAZ cStat=138, mas não veio docZip."

    first = docs[0]
    xml_text = first.get("xml", "")
    schema = first.get("schema", "")
    nsu = first.get("nsu", "")

    # Pode vir 'resNFe' (resumo) dependendo da permissão/autXML
    return True, xml_text, f"OK cStat=138 | schema={schema} | NSU={nsu}"