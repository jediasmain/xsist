from __future__ import annotations

from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
import tempfile
from pathlib import Path


def pfx_to_pem_files(pfx_path: str, pfx_password: str) -> tuple[str, str]:
    pfx_bytes = Path(pfx_path).read_bytes()
    key, cert, _ = load_key_and_certificates(pfx_bytes, pfx_password.encode("utf-8"))

    if key is None or cert is None:
        raise RuntimeError("PFX inválido ou senha incorreta (não encontrei chave/cert).")

    cert_pem = cert.public_bytes(Encoding.PEM)
    key_pem = key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())

    cert_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    key_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    cert_file.write(cert_pem); cert_file.close()
    key_file.write(key_pem); key_file.close()

    return cert_file.name, key_file.name