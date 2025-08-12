# SFTP File Importer Service
A microservice for automated file downloading from SFTP servers with processing capabilities. Provides reliable and parallel processing of large files (up to several GB) with minimal latency.

## Key Features:

    - Periodic scanning of SFTP servers

    - Automatic downloading of new files

    - File metadata storage in PostgreSQL

    - Parallel processing with Celery

    - File status tracking

    - Optimized for large file transfers

    - Secure credential management

## Technology Stack:

    - Programming Language: Python 3.9+

    - Task Queue: Celery + Redis

    - Database: PostgreSQL

    - Message Broker: RabbitMQ (future integration)

    - File Storage: MinIO (future integration)

## Key Libraries:

    - SQLAlchemy (ORM)

    - Paramiko (SFTP client)

    - Alembic (database migrations)

    - Poetry (dependency management)

    - FastAPI (future web interface)

## Getting Started

Prerequisites

    Docker and Docker Compose

    Python 3.9+

    Poetry package manager

1. Clone Repository

```sh
git clone https://github.com/your-username/sftp-importer.git
cd sftp-importer
```

2. Configure Environment

PostgreSQL Configuration:

PG_HOST=localhost

PG_PORT=5432

PG_USER=your_user

PG_PASSWORD=your_password

PG_DB=your_database

3. Install dependencies

```sh
poetry install --no-root
```

4. Apply Database Migrations

```sh
alembic upgrade head
```

5. Run Celery Worker

```sh
poetry run celery -A app.celery_app worker --beat -l INFO -c 4
```

## You can create test sftp server user docker:

1. Create directory for upload files:

```sh
mkdir -p ~/sftp_test/uploads
```

2. Start the container:

```sh
docker run -d --name sftp-server \
    -v ~/sftp_test/uploads:/home/testuser/uploads \
    -p 2222:22 \
    atmoz/sftp \
    testuser:testpass:1001
```

3. Grant testuser permission:

```sh
docker exec sftp-server chown 1001:1001 /home/testuser/uploads
```

4. Use script to add server to database:

```sh
python3 add_sftp.py
```

5. Use script to add files to server:

```sh
bash create_files_script.sh
```

## Project structure

FastApi_sftp_connector/
├── app/                   # Application core

│   ├── celery_app.py      # Celery configuration

│   ├── tasks.py           # Background tasks

│   ├── models.py          # Database models

│   ├── sftp_utils.py      # SFTP utilities

│   ├── periodic.py        # Server scanning routine   

│   ├── config.py          # Application configuration

│   └── __init__.py

├── migrations/            # Database migrations

├── tests/                 # Test suite

├── .env.dev.pg            # Environment variables

├── docker-compose.yml     # Docker configuration

├── pyproject.toml         # Poetry dependencies

├── alembic.ini            # Alembic configuration

└── README.md
