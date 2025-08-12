from app.celery_app import celery_app
from app.tasks import scan_servers


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print("Configuring periodic tasks...")

    sender.add_periodic_task(
        60.0,
        scan_servers.s(),
        name='Scan SFTP servers every minute'
    )

    print("Configured periodic task: Scan SFTP servers every minute")

