# Configuration Guide

This guide will help you configure the Intern Management System for your needs.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Email (Required for certificate sending)**
   - See "Email Configuration" section below

3. **Run the Application**
   ```bash
   python app.py
   ```

4. **Access the System**
   - Open: http://localhost:5000
   - Login: admin / admin123

## Email Configuration

The system uses Gmail SMTP to send certificates. Follow these steps:

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security
3. Enable "2-Step Verification"

### Step 2: Generate App Password
1. Go to Google Account settings → Security
2. Click on "2-Step Verification"
3. Scroll down and click "App passwords"
4. Select "Mail" and "Other (Custom name)"
5. Enter a name like "Intern Management System"
6. Click "Generate"
7. Copy the 16-character password

### Step 3: Update Configuration
Edit `app.py` and update these lines:

```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Your Gmail address
app.config['MAIL_PASSWORD'] = 'your-app-password'     # The 16-character app password
```

### Alternative Email Providers

If you want to use other email providers, update the SMTP settings:

```python
# For Outlook/Hotmail
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587

# For Yahoo
app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
app.config['MAIL_PORT'] = 587

# For custom SMTP
app.config['MAIL_SERVER'] = 'your-smtp-server.com'
app.config['MAIL_PORT'] = 587
```

## Database Configuration

The system uses SQLite by default. To use other databases:

### PostgreSQL
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'
```

### MySQL
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/dbname'
```

## Security Configuration

### Change Default Admin Password
After first login, you can change the admin password by modifying the database or adding a password change feature.

### Secret Key
Change the secret key in `app.py`:
```python
app.config['SECRET_KEY'] = 'your-very-secure-secret-key-here'
```

## Customization

### Certificate Design
Modify the `generate_certificate()` function in `app.py` to customize:
- Certificate layout
- Colors and fonts
- Company logo
- Signature area

### Email Templates
Edit the `send_certificate_email()` function to customize:
- Email subject
- Email body content
- Email formatting

### UI Styling
Modify `templates/base.html` to customize:
- Color scheme
- Layout
- Fonts
- Icons

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Variables
For production, use environment variables:

```python
import os

app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
```

## Troubleshooting

### Email Issues
- **"Authentication failed"**: Check app password and 2FA settings
- **"Connection refused"**: Check firewall and network settings
- **"SSL/TLS required"**: Ensure `MAIL_USE_TLS = True`

### Database Issues
- **"Database locked"**: Restart the application
- **"Table doesn't exist"**: Delete `interns.db` and restart

### Certificate Generation Issues
- **"ReportLab not found"**: Run `pip install reportlab`
- **"Permission denied"**: Check file write permissions

### Port Issues
- **"Port already in use"**: Change port in `app.py`:
  ```python
  app.run(debug=True, port=5001)
  ```

## Performance Optimization

### Database Optimization
- Use PostgreSQL for large datasets
- Add database indexes
- Implement connection pooling

### Email Optimization
- Use email queue system (Celery)
- Implement email templates
- Add email tracking

### Caching
- Implement Redis caching
- Cache certificate templates
- Cache database queries

## Monitoring

### Logging
Add logging to `app.py`:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Health Checks
Add health check endpoint:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy'}
```

## Backup and Recovery

### Database Backup
```bash
# SQLite backup
cp interns.db interns.db.backup

# PostgreSQL backup
pg_dump dbname > backup.sql
```

### Certificate Backup
- Store certificates in cloud storage
- Implement certificate versioning
- Regular backup scheduling

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the README.md file
3. Check Flask and SQLAlchemy documentation
4. Verify email configuration with your provider

