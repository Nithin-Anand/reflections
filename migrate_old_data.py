#!/usr/bin/env python
"""
Migration script to import data from old NiceGUI database to Django.

This script migrates users and journal entries from the old SQLite database
(database/main.db) to the new Django database.
"""

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import django

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "journal_project.settings")
django.setup()

from django.contrib.auth.models import User

from journal.models import JournalEntry


def migrate_data():
    """Migrate data from old database to Django database."""
    old_db_path = Path(__file__).parent / "database" / "main.db"

    if not old_db_path.exists():
        print(f"Old database not found at {old_db_path}")
        print("No data to migrate.")
        return

    # Connect to old database
    old_conn = sqlite3.connect(old_db_path)
    old_conn.row_factory = sqlite3.Row
    old_cursor = old_conn.cursor()

    # Check if tables exist
    old_cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    )
    if not old_cursor.fetchone():
        print("Old database doesn't have a 'users' table. Skipping migration.")
        old_conn.close()
        return

    print("Starting data migration...")

    # Migrate users
    old_cursor.execute("SELECT id, username, password_hash, created_at FROM users")
    old_users = old_cursor.fetchall()

    user_mapping = {}  # Map old user IDs to new User objects
    users_created = 0

    for old_user in old_users:
        username = old_user["username"]

        # Check if user already exists
        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists, skipping...")
            user_mapping[old_user["id"]] = existing_user
            continue

        # Create new user with hashed password from old database
        # Note: Django uses a different password hashing scheme
        # Users will need to reset their passwords
        new_user = User.objects.create_user(
            username=username, password=f"temp_{username}_password"
        )
        new_user.date_joined = datetime.fromisoformat(old_user["created_at"])
        new_user.save()

        user_mapping[old_user["id"]] = new_user
        users_created += 1
        print(f"Created user: {username}")

    # Migrate journal entries
    old_cursor.execute(
        "SELECT id, user_id, timestamp, content FROM journal ORDER BY timestamp"
    )
    old_entries = old_cursor.fetchall()

    entries_created = 0
    for old_entry in old_entries:
        if old_entry["user_id"] not in user_mapping:
            print(f"Skipping entry for unknown user_id: {old_entry['user_id']}")
            continue

        user = user_mapping[old_entry["user_id"]]
        timestamp = datetime.fromisoformat(old_entry["timestamp"])

        # Check if entry already exists (avoid duplicates)
        existing_entry = JournalEntry.objects.filter(
            user=user, timestamp=timestamp, content=old_entry["content"]
        ).first()

        if existing_entry:
            print(
                f"Entry already exists for {user.username} at {timestamp}, skipping..."
            )
            continue

        # Create new journal entry
        entry = JournalEntry(
            user=user, content=old_entry["content"], timestamp=timestamp
        )
        entry.save()
        entries_created += 1

    old_conn.close()

    print("\nMigration complete!")
    print(f"- Users created: {users_created}")
    print(f"- Journal entries created: {entries_created}")
    print("\nNote: Migrated users have temporary passwords.")
    print("Users should reset their passwords through the admin interface.")


if __name__ == "__main__":
    migrate_data()
