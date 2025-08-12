from app.models import Server
from app.config import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(get_database_url())
Session = sessionmaker(bind=engine)
db = Session()

server = Server(
    host="localhost",
    port=2222,
    username="testuser",
    password="testpass",
    remote_path="/uploads"
)


db.add(server)
db.commit()
print(f"Added test server ID: {server.id}")
