import zipfile
from io import BytesIO
from pathlib import Path

def build_extension_zip() -> bytes:
    repo_root = Path(__file__).resolve().parents[1]  # raiz do projeto
    ext_dir = repo_root / "chrome_ext"

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in ext_dir.rglob("*"):
            if p.is_file():
                # cria zip com uma pasta "chrome_ext" dentro
                z.write(p, arcname=f"chrome_ext/{p.relative_to(ext_dir)}")
    return buf.getvalue()

st.divider()
st.subheader("Instalar Extensão (download)")

st.download_button(
    "Baixar XSist Connector (ZIP)",
    data=build_extension_zip(),
    file_name="xsist_connector_chrome_ext.zip",
    mime="application/zip",
    use_container_width=True,
)

st.info(
    "Como instalar (Chrome):\n"
    "1) Baixe o ZIP e descompacte\n"
    "2) Abra chrome://extensions\n"
    "3) Ative 'Modo do desenvolvedor'\n"
    "4) Clique 'Carregar sem compactação'\n"
    "5) Selecione a pasta descompactada: chrome_ext"
)