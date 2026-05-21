from __future__ import annotations

import argparse

from app import app
from migrations import get_migration_status, run_migrations


def main() -> int:
    parser = argparse.ArgumentParser(description='Bookmark System backend management')
    parser.add_argument(
        'command',
        choices=['migrate', 'migration-status'],
        help='Command to run',
    )
    args = parser.parse_args()

    with app.app_context():
        if args.command == 'migrate':
            applied = run_migrations()
            if applied:
                print('Applied migrations: ' + ', '.join(applied))
            else:
                print('No pending migrations.')
            return 0

        for item in get_migration_status():
            status = 'applied' if item['applied'] else 'pending'
            print(f"{item['version']} {item['name']} [{status}]")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
