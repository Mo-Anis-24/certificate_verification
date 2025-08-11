#!/usr/bin/env python3
"""
Setup script for Intern Management System
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error: Failed to install dependencies")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = ["templates"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def check_files():
    """Check if all required files exist"""
    required_files = [
        "app.py",
        "requirements.txt",
        "templates/base.html",
        "templates/login.html",
        "templates/dashboard.html",
        "templates/add_intern.html"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Error: Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        sys.exit(1)
    
    print("✅ All required files found")

def create_config_template():
    """Create a configuration template"""
    config_content = """# Email Configuration
# Update these settings in app.py

# Gmail Settings
MAIL_USERNAME = 'your-email@gmail.com'  # Your Gmail address
MAIL_PASSWORD = 'your-app-password'     # Your Gmail app password

# To get Gmail app password:
# 1. Enable 2-factor authentication on your Gmail account
# 2. Go to Google Account settings → Security → 2-Step Verification → App passwords
# 3. Generate a new app password
# 4. Use that password here (not your regular Gmail password)

# Default Admin Credentials
# Username: admin
# Password: admin123
"""
    
    with open("config_template.txt", "w") as f:
        f.write(config_content)
    print("📝 Created config_template.txt with setup instructions")

def main():
    """Main setup function"""
    print("🚀 Setting up Intern Management System...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check files
    check_files()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Create config template
    create_config_template()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure email settings in app.py")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("4. Login with: admin / admin123")
    print("\n📖 See README.md for detailed instructions")

if __name__ == "__main__":
    main()

