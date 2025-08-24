#!/usr/bin/env python3
"""
Database reset script to remove existing admin accounts
Run this script to clear the database and start fresh
"""

from app import app, db, Admin

def reset_database():
    with app.app_context():
        # Delete all existing admin accounts
        Admin.query.delete()
        db.session.commit()
        print("All admin accounts have been removed from the database.")
        print("You can now register the first admin through the web interface.")

if __name__ == '__main__':
    confirm = input("This will delete ALL admin accounts. Are you sure? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("Database reset cancelled.")
