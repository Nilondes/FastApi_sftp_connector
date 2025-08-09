import os

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, File, FileStatus, Server
from .sftp_utils import sftp_connection, download_file


from .config import get_database_url

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)


@celery_app.task(bind=True, max_retries=3)
def download_sftp_file(self, server_id, filename):
    db = SessionLocal()
    try:
        file_record = db.query(File).filter(
            File.server_id == server_id,
            File.filename == filename,
            File.status == FileStatus.NEW
        ).first()

        if not file_record:
            return

        file_record.status = FileStatus.DOWNLOADING
        db.commit()

        server = db.query(Server).filter(Server.id == server_id).first()
        if not server:
            raise ValueError(f"Server {server_id} not found")

        temp_dir = "/tmp/sftp_downloads"
        os.makedirs(temp_dir, exist_ok=True)
        local_path = os.path.join(temp_dir, filename)

        with sftp_connection(
                server.host,
                server.port,
                server.username,
                server.password
        ) as sftp:
            remote_path = os.path.join(server.remote_path, filename)
            download_file(sftp, remote_path, local_path)

        file_record.status = FileStatus.DOWNLOADED
        db.commit()

    except Exception as e:
        file_record.status = FileStatus.ERROR
        db.rollback()
        db.commit()
        self.retry(exc=e, countdown=60)
    finally:
        db.close()
