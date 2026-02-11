from sqlalchemy import select
from data.db import SessionLocal
from data.models import DownloadEvent

def add_event(chave, tipo, status, mensagem="") -> int:
    db = SessionLocal()
    try:
        ev = DownloadEvent(chave=chave, tipo=tipo, status=status, mensagem=mensagem)
        db.add(ev)
        db.commit()
        db.refresh(ev)  # garante que o ev.id vem preenchido
        return ev.id
    finally:
        db.close()

def list_events(limit=200):
    db = SessionLocal()
    try:
        stmt = select(DownloadEvent).order_by(DownloadEvent.id.desc()).limit(limit)
        rows = db.execute(stmt).scalars().all()
        return [{
            "id": r.id,
            "chave": r.chave,
            "tipo": r.tipo,
            "status": r.status,
            "mensagem": r.mensagem,
            "created_at": r.created_at,
        } for r in rows]
    finally:
        db.close()

from data.models import XmlDoc  # (se já tiver DownloadEvent importado, mantém os dois)

def save_xml_doc(chave: str, tipo: str, xml_text: str) -> None:
    db = SessionLocal()
    try:
        stmt = select(XmlDoc).where(XmlDoc.chave == chave, XmlDoc.tipo == tipo)
        existing = db.execute(stmt).scalar_one_or_none()

        if existing:
            existing.xml_text = xml_text
        else:
            db.add(XmlDoc(chave=chave, tipo=tipo, xml_text=xml_text))

        db.commit()
    finally:
        db.close()


def list_xml_docs(limit: int = 200) -> list[dict]:
    db = SessionLocal()
    try:
        stmt = select(XmlDoc).order_by(XmlDoc.id.desc()).limit(limit)
        rows = db.execute(stmt).scalars().all()
        return [
            {"id": r.id, "chave": r.chave, "tipo": r.tipo, "created_at": r.created_at}
            for r in rows
        ]
    finally:
        db.close()


def get_xml_doc(doc_id: int) -> dict | None:
    db = SessionLocal()
    try:
        doc = db.get(XmlDoc, doc_id)
        if not doc:
            return None
        return {"id": doc.id, "chave": doc.chave, "tipo": doc.tipo, "xml_text": doc.xml_text}
    finally:
        db.close()

def update_event(event_id: int, status: str, mensagem: str = "") -> None:
    db = SessionLocal()
    try:
        ev = db.get(DownloadEvent, event_id)
        if not ev:
            return
        ev.status = status
        ev.mensagem = mensagem
        db.commit()
    finally:
        db.close()