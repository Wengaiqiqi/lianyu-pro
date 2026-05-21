from __future__ import annotations

from datetime import datetime

from sqlalchemy import inspect, text

from models import db
from .revisions import MIGRATIONS


MIGRATIONS_TABLE = 'schema_migrations'


def _ensure_migrations_table() -> None:
    inspector = inspect(db.engine)
    if MIGRATIONS_TABLE in inspector.get_table_names():
        return

    with db.engine.begin() as connection:
        connection.execute(
            text(
                f'''
                CREATE TABLE {MIGRATIONS_TABLE} (
                    version VARCHAR(64) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    applied_at DATETIME NOT NULL
                )
                '''
            )
        )


def _applied_versions() -> set[str]:
    rows = db.session.execute(
        text(f'SELECT version FROM {MIGRATIONS_TABLE}')
    ).fetchall()
    return {row[0] for row in rows}


def get_migration_status() -> list[dict]:
    _ensure_migrations_table()
    applied_versions = _applied_versions()
    return [
        {
            'version': migration.version,
            'name': migration.name,
            'applied': migration.version in applied_versions,
        }
        for migration in MIGRATIONS
    ]


def run_migrations() -> list[str]:
    _ensure_migrations_table()
    applied_versions = _applied_versions()
    applied_now: list[str] = []

    for migration in MIGRATIONS:
        if migration.version in applied_versions:
            continue

        with db.engine.begin() as connection:
            migration.upgrade(connection)
            connection.execute(
                text(
                    f'''
                    INSERT INTO {MIGRATIONS_TABLE} (version, name, applied_at)
                    VALUES (:version, :name, :applied_at)
                    '''
                ),
                {
                    'version': migration.version,
                    'name': migration.name,
                    'applied_at': datetime.utcnow(),
                }
            )

        applied_now.append(migration.version)
        applied_versions.add(migration.version)

    return applied_now
