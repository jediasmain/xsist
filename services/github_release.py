from __future__ import annotations

import requests


def get_latest_release_asset_url(
    owner: str,
    repo: str,
    asset_name: str,
    token: str | None = None,
) -> str | None:
    """
    Retorna a URL direta (browser_download_url) do asset no release 'latest'.
    Ex.: asset_name="XSistConnector.zip"

    Se não achar ou falhar, retorna None.
    """
    api = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

    headers = {"User-Agent": "xsist-streamlit-app"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        r = requests.get(api, headers=headers, timeout=30)
    except Exception:
        return None

    if r.status_code != 200:
        return None

    data = r.json()
    assets = data.get("assets", [])
    for a in assets:
        if a.get("name") == asset_name:
            return a.get("browser_download_url")

    return None