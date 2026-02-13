import streamlit as st

st.set_page_config(page_title="Ajuda - XSist", layout="wide")
st.title("Ajuda / Como usar (XSist)")

st.write(
    "O XSist funciona no estilo FSist:\n"
    "- O site roda na internet (Streamlit Cloud)\n"
    "- O download acontece no seu computador via **Extensão do Chrome**\n"
    "- A extensão conversa com um programa local chamado **Conector** (porta 127.0.0.1:8765)\n"
)

st.divider()

st.header("1) Instalar a Extensão do Chrome")
st.write(
    "1) Vá na página **Setup** do site\n"
    "2) Baixe o ZIP da extensão\n"
    "3) Descompacte (vai aparecer uma pasta chamada `chrome_ext`)\n"
    "4) Abra no Chrome: `chrome://extensions`\n"
    "5) Ative **Modo do desenvolvedor**\n"
    "6) Clique **Carregar sem compactação**\n"
    "7) Selecione a pasta `chrome_ext`\n"
    "8) Fixe o ícone da extensão (pino/alfinete) para ficar visível na barra do Chrome\n"
)

st.info(
    "Dica: ao selecionar a pasta no Chrome, às vezes a janela mostra a pasta 'vazia'. "
    "Isso é normal (ela não lista arquivos). Se a pasta tiver `manifest.json`, clique em **Selecionar pasta**."
)

st.divider()

st.header("2) Instalar / Rodar o Conector (Windows)")
st.write(
    "1) Vá na página **Setup** do site\n"
    "2) Baixe o **XSistConnector (ZIP)**\n"
    "3) Extraia o ZIP\n"
    "4) Execute `XSistConnector.exe`\n"
    "5) Deixe a janela aberta (o conector precisa ficar rodando)\n"
)

st.write("Teste rápido:")
st.code("http://127.0.0.1:8765/ping", language="text")
st.write("Se abrir e mostrar JSON `ok:true`, o conector está ligado.")

st.divider()

st.header("3) Verificar se está tudo OK (Setup)")
st.write(
    "1) Abra a página **Setup**\n"
    "2) Clique **Atualizar status**\n"
    "3) Você deve ver:\n"
    "- Extensão detectada ✅\n"
    "- Conector respondeu ✅\n"
)

st.divider()

st.header("4) Configurar Certificado A1 (para baixar da SEFAZ de verdade)")
st.warning(
    "Para baixar XML oficial da SEFAZ, é obrigatório ter um certificado digital A1 (.pfx/.p12) "
    "válido e com permissão para o documento (emitente/destinatário/autXML)."
)

st.write(
    "1) Clique no ícone da extensão **XSist Connector** (na barra do Chrome)\n"
    "2) Na área 'Configurar Certificado A1':\n"
    "- selecione o arquivo `.pfx/.p12`\n"
    "- digite a senha\n"
    "- digite o CNPJ (14 dígitos)\n"
    "3) Clique **Salvar certificado no conector**\n"
    "4) Volte no **Setup** e clique **Atualizar status**\n"
)

st.divider()

st.header("5) Baixar XML")
st.write(
    "1) Vá na página **Download**\n"
    "2) Selecione o tipo (NFE/CTE)\n"
    "3) Cole a chave (44 dígitos)\n"
    "4) Clique **Baixar 1 XML via Extensão**\n"
)

st.info(
    "Se não baixar, veja a seção 'Último retorno (debug)' na página Download "
    "e confira se o certificado A1 foi configurado."
)

st.divider()

st.header("Problemas comuns")
st.write(
    "- **Conector não responde / Failed to fetch**: o conector (EXE) não está rodando.\n"
    "- **Extensão não detectada**: recarregue a extensão em `chrome://extensions` e dê F5 no site.\n"
    "- **Não baixa da SEFAZ**: falta A1 configurado ou o certificado não tem permissão/autXML.\n"
    "- **Chave inválida**: precisa ter exatamente 44 dígitos.\n"
)