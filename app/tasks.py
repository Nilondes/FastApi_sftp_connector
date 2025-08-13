from app.celery_app import celery_app, engine
from app.models import Server, File, FileStatus
from app.sftp_utils import sftp_connection, download_file
from sqlalchemy.orm import sessionmaker
import os
import logging


logger = logging.getLogger(__name__)

Session = sessionmaker(bind=engine)


@celery_app.task(name='app.tasks.scan_servers')
def scan_servers():
    logger.info("=== STARTING SERVER SCAN ===")
    db = Session()
    try:
        servers = db.query(Server).all()
        logger.info(f"Found {len(servers)} servers to scan")

        for server in servers:
            logger.info(f"Scanning server {server.id} at {server.host}:{server.port}")

            try:
                with sftp_connection(
                        server.host,
                        server.port,
                        server.username,
                        server.password
                ) as sftp:
                    logger.info(f"Connected to server {server.id}")

                    try:
                        sftp.stat(server.remote_path)
                        logger.info(f"Path exists: {server.remote_path}")
                        remote_files = sftp.listdir(server.remote_path)
                        logger.info(f"Found {len(remote_files)} files")
                    except FileNotFoundError:
                        logger.error(f"Path not found: {server.remote_path}")
                        remote_files = []

                    existing_files = {f.filename for f in server.files}
                    new_files = [f for f in remote_files if f not in existing_files]
                    logger.info(f"Found {len(new_files)} new files")

                    for filename in new_files:
                        logger.info(f"Adding new file: {filename}")
                        new_file = File(
                            server_id=server.id,
                            filename=filename,
                            status=FileStatus.NEW
                        )
                        db.add(new_file)
                        db.commit()
                        logger.info(f"Triggering download for {filename}")
                        download_sftp_file.delay(server.id, filename)
            except Exception as e:
                logger.error(f"Error scanning server {server.id}: {str(e)}")
    except Exception as e:
        logger.error(f"General scan error: {str(e)}")
    finally:
        db.close()
        logger.info("=== SERVER SCAN COMPLETED ===")


@celery_app.task(bind=True, max_retries=3)
def download_sftp_file(self, server_id, filename):
    logger.info(f"Starting download of {filename} from server {server_id}")
    db = Session()
    try:
        file_record = db.query(File).filter(
            File.server_id == server_id,
            File.filename == filename,
            File.status == FileStatus.NEW
        ).first()

        if not file_record:
            logger.warning(f"File record not found: {filename}")
            return

        file_record.status = FileStatus.DOWNLOADING
        db.commit()

        server = db.query(Server).get(server_id)
        if not server:
            logger.error(f"Server {server_id} not found")
            return

        dir = "sftp_downloads"
        os.makedirs(dir, exist_ok=True)
        local_path = os.path.join(dir, filename)

        with sftp_connection(
                server.host,
                server.port,
                server.username,
                server.password
        ) as sftp:
            remote_path = os.path.join(server.remote_path, filename)
            logger.info(f"Downloading {remote_path} to {local_path}")
            file_size = download_file(sftp, remote_path, local_path)
            logger.info(f"Downloaded {filename} ({file_size} bytes)")
            logger.info(f"Full local path: {os.path.abspath(local_path)}")

        file_record.status = FileStatus.DOWNLOADED
        db.commit()
        logger.info(f"File {filename} marked as downloaded")

    except Exception as e:
        logger.error(f"Error downloading {filename}: {str(e)}")
        if file_record:
            file_record.status = FileStatus.ERROR
            db.commit()

        self.retry(exc=e, countdown=60)
    finally:
        db.close()
