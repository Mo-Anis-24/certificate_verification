# Admin System Setup Guide

## Overview
The certificate verification system now has a secure admin management system where:
- The first admin can register directly when no admin exists
- After the first admin is created, only existing admins can add new admins
- Default admin credentials have been removed for security

## Initial Setup

### Option 1: Fresh Installation (Recommended)
1. Delete the existing `instance/interns.db` file
2. Run the application: `python app.py`
3. Navigate to the login page
4. You'll see a "Register First Admin" button
5. Click it and create your first admin account
6. Login with your new credentials

### Option 2: Reset Existing Database
If you have an existing database with default admin accounts:
1. Run the reset script: `python reset_db.py`
2. Confirm the reset when prompted
3. Follow steps 3-6 from Option 1

## Admin Management

### Adding New Admins
1. Login as an existing admin
2. Go to "Choose Panel" → "Admin Management"
3. Click "Add New Admin"
4. Fill in the username and password
5. Submit the form

### Deleting Admins
1. Go to Admin Management panel
2. Click "Delete" next to the admin you want to remove
3. Confirm the deletion
4. Note: You cannot delete your own account or the last admin

## Security Features
- Password confirmation required for all admin creation
- Username uniqueness enforced
- Cannot delete the last admin account
- Cannot delete your own account
- All admin operations require authentication

## File Structure
- `app.py` - Main application with admin routes
- `templates/admin_register.html` - First admin registration
- `templates/admin_management.html` - Admin management panel
- `templates/add_admin.html` - Add new admin form
- `reset_db.py` - Database reset utility

## Routes
- `/admin_register` - First admin registration (only accessible when no admin exists)
- `/admin_management` - Admin management panel (requires login)
- `/add_admin` - Add new admin form (requires login)
- `/delete_admin/<id>` - Delete admin (requires login)

## Troubleshooting
- If you get locked out, delete the database file and start fresh
- Ensure all template files are in the correct location
- Check that Flask-Login is properly configured
- Verify database permissions and file paths
