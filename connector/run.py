from __future__ import annotations

import sys
from pathlib import Path

# garante que a raiz do projeto entra no PATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import uvicorn
from connector.main import app  # IMPORT REAL (isso faz o PyInstaller incluir o pacote)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765, reload=False)