from __future__ import annotations

from services.sefaz_nfe import download_nfe_xml_by_key_official


def download_xml_by_key(
    chave: str,
    tipo: str,
    *,
    pfx_path: str | None = None,
    pfx_password: str | None = None,
    cnpj: str | None = None,
    tp_amb: int = 1,
) -> tuple[bool, str | None, str]:
    tipo = (tipo or "").upper()

    if tipo == "NFE":
        return download_nfe_xml_by_key_official(
            chave=chave,
            pfx_path=pfx_path,
            pfx_password=pfx_password,
            cnpj=cnpj,
            tp_amb=tp_amb,
        )

    if tipo == "CTE":
        return False, None, "CT-e oficial ainda não implementado nesta fase."

    return False, None, "Tipo inválido (use NFE ou CTE)."