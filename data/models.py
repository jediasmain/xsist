from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text
from data.db import Base

class DownloadEvent(Base):
    __tablename__ = "downloads"

    id: Mapped[int] = mapped_column(primary_key=True)
    chave: Mapped[str] = mapped_column(String(44), index=True)
    tipo: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))
    mensagem: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class XmlDoc(Base):
    __tablename__ = "xml_docs"

    id: Mapped[int] = mapped_column(primary_key=True)
    chave: Mapped[str] = mapped_column(String(60), index=True)
    tipo: Mapped[str] = mapped_column(String(10))  # NFE / CTE
    xml_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)