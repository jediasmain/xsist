from __future__ import annotations

import base64
import json
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

from services.sefaz import download_xml_by_key

app = FastAPI()

BASE_DIR = Path.home() / ".xsist"
BASE_DIR.mkdir(parents=True, exist_ok=True)

CERT_PATH = BASE_DIR / "cert.pfx"
CFG_PATH = BASE_DIR / "config.json"


class CertConfigReq(BaseModel):
    pfx_b64: str
    password: str
    cnpj: str = ""
    tp_amb: int = 1  # 1=produção, 2=homologação


class DownloadReq(BaseModel):
    chave: str
    tipo: str  # NFE / CTE


def so_digitos(s: str) -> str:
    return "".join(c for c in (s or "") if c.isdigit())


def load_cfg() -> dict:
    if CFG_PATH.exists():
        return json.loads(CFG_PATH.read_text(encoding="utf-8"))
    return {}


def save_cfg(cfg: dict) -> None:
    CFG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def verify_pfx_bytes(pfx_bytes: bytes, password: str) -> tuple[bool, str]:
    """
    Verifica se o PFX abre com a senha e se existe chave privada.
    """
    try:
        key, cert, _ = load_key_and_certificates(pfx_bytes, password.encode("utf-8"))
        if key is None or cert is None:
            return False, "PFX não contém chave privada/certificado (ou senha errada)."
        subj = cert.subject.rfc4514_string()
        return True, f"OK: certificado lido. Subject={subj}"
    except Exception as e:
        return False, f"Falha ao ler PFX (senha errada ou arquivo inválido): {e}"


@app.get("/ping")
def ping():
    return {"ok": True, "msg": "Conector local rodando"}


@app.get("/status")
def status():
    cfg = load_cfg()
    return {
        "ok": True,
        "has_cert": CERT_PATH.exists(),
        "has_password": bool(cfg.get("pfx_password")),
        "has_cnpj": bool(cfg.get("cnpj")),
        "tp_amb": cfg.get("tp_amb", 1),
    }


@app.get("/cert/verify")
def cert_verify():
    cfg = load_cfg()
    if not CERT_PATH.exists():
        return {"ok": False, "msg": "Ainda não há cert.pfx salvo no conector."}
    if not cfg.get("pfx_password"):
        return {"ok": False, "msg": "Não há senha salva no conector."}

    ok, msg = verify_pfx_bytes(CERT_PATH.read_bytes(), cfg["pfx_password"])
    return {"ok": ok, "msg": msg}


@app.post("/config/cert")
def config_cert(req: CertConfigReq):
    if not req.password:
        return {"ok": False, "msg": "Senha do certificado é obrigatória."}

    pfx_bytes = base64.b64decode(req.pfx_b64)

    # valida ANTES de salvar
    ok, msg = verify_pfx_bytes(pfx_bytes, req.password)
    if not ok:
        return {"ok": False, "msg": msg}

    CERT_PATH.write_bytes(pfx_bytes)

    cfg = load_cfg()
    cfg["pfx_path"] = str(CERT_PATH)
    cfg["pfx_password"] = req.password
    cfg["cnpj"] = so_digitos(req.cnpj)
    cfg["tp_amb"] = int(req.tp_amb or 1)
    save_cfg(cfg)

    return {"ok": True, "msg": "Certificado salvo e validado no conector local."}


@app.post("/download")
def download(req: DownloadReq):
    cfg = load_cfg()
    pfx_path = cfg.get("pfx_path") or (str(CERT_PATH) if CERT_PATH.exists() else "")
    pfx_password = cfg.get("pfx_password", "")
    cnpj = cfg.get("cnpj", "")
    tp_amb = int(cfg.get("tp_amb", 1))

    ok, xml_text, msg = download_xml_by_key(
        chave=req.chave,
        tipo=req.tipo,
        pfx_path=pfx_path,
        pfx_password=pfx_password,
        cnpj=cnpj,
        tp_amb=tp_amb,
    )

    if not ok or not xml_text:
        return {"ok": False, "msg": msg}

    return {"ok": True, "msg": msg, "xml": xml_text}