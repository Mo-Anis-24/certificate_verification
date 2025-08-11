# Intern Management System

A Flask-based web application for managing interns and generating certificates. This system allows administrators to add intern details, approve/reject applications, and automatically send certificates via email.

## Features

- **Admin Authentication**: Secure login system for administrators
- **Intern Management**: Add, view, and manage intern details
- **Certificate Generation**: Automatic PDF certificate generation
- **Email Integration**: Send certificates directly to intern email addresses
- **Status Tracking**: Track intern status (pending, approved, rejected)
- **Modern UI**: Beautiful, responsive interface with Bootstrap 5
- **Dashboard Statistics**: Overview of intern statistics

## Screenshots

### Login Page
- Clean, modern login interface
- Default credentials provided

### Dashboard
- Complete intern management table
- Action buttons for approve/reject
- Status indicators
- Statistics cards

### Add Intern Form
- User-friendly form with validation
- Date picker for joining and end dates
- Email validation

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   # If you have the files, skip this step
   git clone <repository-url>
   cd certificate_ganrator
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure email settings**
   
   Edit `app.py` and update the email configuration:
   ```python
   app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Your Gmail address
   app.config['MAIL_PASSWORD'] = 'your-app-password'     # Your Gmail app password
   ```
   
   **Note**: For Gmail, you need to:
   - Enable 2-factor authentication
   - Generate an App Password
   - Use the App Password instead of your regular password

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Login with default credentials:
     - Username: `admin`
     - Password: `admin123`

## Usage Guide

### 1. Login
- Use the default credentials or create a new admin account
- The system will automatically create the admin user on first run

### 2. Add Interns
- Click "Add New Intern" from the dashboard
- Fill in all required fields:
  - Full Name
  - Email Address
  - Joining Date
  - End Date
- Click "Add Intern"

### 3. Manage Interns
- View all interns in the dashboard table
- Each intern starts with "Pending" status
- Use action buttons to approve or reject interns

### 4. Approve Interns
- Click "Approve" button for pending interns
- System will automatically:
  - Generate a PDF certificate
  - Send it to the intern's email
  - Update the status to "Approved"
  - Mark certificate as sent

### 5. Download Certificates
- For approved interns, you can download certificates manually
- Click "Download Certificate" button

## File Structure

```
certificate_ganrator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with styling
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   └── add_intern.html  # Add intern form
└── interns.db           # SQLite database (created automatically)
```

## Database Schema

### Admin Table
- `id`: Primary key
- `username`: Admin username
- `password_hash`: Hashed password

### Intern Table
- `id`: Primary key
- `name`: Intern's full name
- `email`: Intern's email address
- `joining_date`: Internship start date
- `end_date`: Internship end date
- `status`: Current status (pending/approved/rejected)
- `certificate_sent`: Boolean flag for certificate status

## Email Configuration

The application uses Gmail SMTP for sending certificates. To configure:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password
3. **Update the configuration** in `app.py`:
   ```python
   app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
   app.config['MAIL_PASSWORD'] = 'your-app-password'
   ```

## Certificate Features

- **Professional Design**: Clean, professional certificate layout
- **Dynamic Content**: Includes intern details and dates
- **PDF Format**: High-quality PDF generation
- **Email Attachment**: Automatically attached to approval emails

## Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for secure sessions
- **Input Validation**: Form validation and sanitization
- **SQL Injection Protection**: SQLAlchemy ORM protection

## Customization

### Styling
- Edit `templates/base.html` to modify the design
- CSS is included in the base template
- Uses Bootstrap 5 for responsive design

### Certificate Design
- Modify the `generate_certificate()` function in `app.py`
- Uses ReportLab for PDF generation
- Customizable layout and styling

### Email Templates
- Edit the `send_certificate_email()` function
- Customize email subject and body content

## Troubleshooting

### Common Issues

1. **Email not sending**
   - Check Gmail app password configuration
   - Ensure 2-factor authentication is enabled
   - Verify email credentials in `app.py`

2. **Database errors**
   - Delete `interns.db` file and restart
   - Database will be recreated automatically

3. **Port already in use**
   - Change port in `app.py`: `app.run(debug=True, port=5001)`

4. **Certificate generation errors**
   - Ensure ReportLab is installed: `pip install reportlab`
   - Check file permissions

### Debug Mode
The application runs in debug mode by default. For production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

