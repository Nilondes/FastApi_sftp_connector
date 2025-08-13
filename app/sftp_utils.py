import paramiko
import os
from contextlib import contextmanager

@contextmanager
def sftp_connection(host, port, username, password):
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        yield sftp
    finally:
        sftp.close()
        transport.close()


def download_file(sftp, remote_path, local_path):
    sftp.get(remote_path, local_path)
    return os.path.getsize(local_path)
