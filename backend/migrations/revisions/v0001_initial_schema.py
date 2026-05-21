from models import db

version = '0001'
name = 'initial_schema'


def upgrade(connection) -> None:
    db.metadata.create_all(bind=connection)
