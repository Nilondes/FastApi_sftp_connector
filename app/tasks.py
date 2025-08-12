from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import File, Server, FileStatus
from .sftp_utils import sftp_connection

from .celery_app import celery_app
from .config import get_database_url

engine = create_engine(get_database_url())
Session = sessionmaker(bind=engine)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        60.0,
        scan_servers.s(),
        name='Scan SFTP servers'
    )


@celery_app.task
def scan_servers():
    db = Session()
    try:
        servers = db.query(Server).all()
        for server in servers:
            with sftp_connection(
                    server.host,
                    server.port,
                    server.username,
                    server.password
            ) as sftp:
                remote_files = sftp.listdir(server.remote_path)
                existing_files = {f.filename for f in server.files}

                for filename in remote_files:
                    if filename not in existing_files:
                        new_file = File(
                            server_id=server.id,
                            filename=filename,
                            status=FileStatus.NEW
                        )
                        db.add(new_file)
                        db.commit()
                        download_sftp_file.delay(server.id, filename)
    finally:
        db.close()