from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class Server(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=22)
    username = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    remote_path = Column(String(255), nullable=False)
    files = relationship("File", back_populates="server")


class FileStatus(enum.Enum):
    NEW = "NEW"
    DOWNLOADING = "DOWNLOADING"
    DOWNLOADED = "DOWNLOADED"
    ERROR = "ERROR"


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(Enum(FileStatus), default=FileStatus.NEW)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    server = relationship("Server", back_populates="files")
