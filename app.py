from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interns.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'your-app-password'     # Replace with your 16-character app password

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Intern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    certificate_sent = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

def generate_certificate(intern):
    """Generate a professional certificate PDF for the intern"""
    buffer = io.BytesIO()
    # Use landscape orientation for better layout
    doc = SimpleDocTemplate(buffer, pagesize=(11*inch, 8.5*inch))
    styles = getSampleStyleSheet()
    story = []
    
    # Define colors
    dark_blue = colors.Color(0.1, 0.2, 0.5)
    bright_green = colors.Color(0.2, 0.8, 0.4)
    gold = colors.Color(0.8, 0.6, 0.2)
    
    # Border decoration (top and bottom strips)
    border_style = ParagraphStyle(
        'Border',
        parent=styles['Normal'],
        fontSize=1,
        textColor=dark_blue,
        alignment=1
    )
    
    # Add top border
    story.append(Paragraph("_" * 100, border_style))
    story.append(Spacer(1, 10))
    
    # Header section with logo and company name
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=16,
        alignment=1,
        spaceAfter=20
    )
    
    # Company name with different colors
    company_name = f'<span color="{dark_blue}">BROADER</span> <span color="{bright_green}">AI</span>'
    story.append(Paragraph(company_name, header_style))
    
    # Tagline
    tagline_style = ParagraphStyle(
        'Tagline',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=dark_blue,
        spaceAfter=30
    )
    story.append(Paragraph("TOWARDS AUTOMATION", tagline_style))
    
    # Main certificate title
    cert_title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        fontSize=28,
        alignment=1,
        textColor=dark_blue,
        spaceAfter=40,
        spaceBefore=20
    )
    story.append(Paragraph("CERTIFICATE", cert_title_style))
    
    # Certificate content
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=14,
        alignment=0,
        spaceAfter=15,
        leftIndent=50,
        rightIndent=50
    )
    
    story.append(Paragraph(f"This is to certify that <b>{intern.name}</b>", content_style))
    story.append(Paragraph("has successfully completed their internship program at BROADER AI.", content_style))
    story.append(Spacer(1, 20))
    
    # Internship details in a professional table
    details_data = [
        ['Intern Name:', intern.name],
        ['Email Address:', intern.email],
        ['Joining Date:', intern.joining_date.strftime('%B %d, %Y')],
        ['End Date:', intern.end_date.strftime('%B %d, %Y')],
        ['Duration:', f"{(intern.end_date - intern.joining_date).days} days"],
        ['Status:', 'Approved']
    ]
    
    details_table = Table(details_data, colWidths=[2.5*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.95, 0.95, 0.95)),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (-1, 0), dark_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, dark_blue),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.98, 0.98, 0.98)])
    ]))
    story.append(details_table)
    story.append(Spacer(1, 40))
    
    # Signature section with professional layout
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        spaceAfter=5
    )
    
    # Signature line
    story.append(Paragraph("_" * 40, signature_style))
    
    # Founder name and title
    founder_style = ParagraphStyle(
        'Founder',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        textColor=dark_blue,
        spaceAfter=5
    )
    
    story.append(Paragraph("MOHAMMAD SOAEB RATHOD", founder_style))
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        textColor=dark_blue,
        spaceAfter=20
    )
    
    story.append(Paragraph("FOUNDER", title_style))
    
    # Date
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.grey
    )
    
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", date_style))
    
    # Add bottom border
    story.append(Spacer(1, 10))
    story.append(Paragraph("_" * 100, border_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def send_certificate_email(intern, certificate_buffer):
    """Send certificate via email"""
    try:
        msg = Message(
            subject='BROADER AI - Your Internship Certificate',
            sender=app.config['MAIL_USERNAME'],
            recipients=[intern.email]
        )
        msg.body = f"""
Dear {intern.name},

Congratulations! Your internship at BROADER AI has been successfully completed and approved.

Your professional certificate is attached to this email.

Internship Details:
- Intern Name: {intern.name}
- Email: {intern.email}
- Joining Date: {intern.joining_date.strftime('%B %d, %Y')}
- End Date: {intern.end_date.strftime('%B %d, %Y')}
- Duration: {(intern.end_date - intern.joining_date).days} days
- Status: Approved

We appreciate your dedication and contribution during your internship period.

Best regards,
BROADER AI Team
MOHAMMAD SOAEB RATHOD
Founder
        """
        
        certificate_buffer.seek(0)
        msg.attach(
            filename=f"BROADER_AI_Certificate_{intern.name.replace(' ', '_')}.pdf",
            content_type="application/pdf",
            data=certificate_buffer.read()
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    interns = Intern.query.all()
    return render_template('dashboard.html', interns=interns)

@app.route('/add_intern', methods=['GET', 'POST'])
@login_required
def add_intern():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        joining_date = datetime.strptime(request.form['joining_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        
        intern = Intern(
            name=name,
            email=email,
            joining_date=joining_date,
            end_date=end_date
        )
        db.session.add(intern)
        db.session.commit()
        flash('Intern added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('add_intern.html')

@app.route('/approve_intern/<int:intern_id>')
@login_required
def approve_intern(intern_id):
    intern = Intern.query.get_or_404(intern_id)
    intern.status = 'approved'
    
    # Generate and send certificate
    certificate_buffer = generate_certificate(intern)
    if send_certificate_email(intern, certificate_buffer):
        intern.certificate_sent = True
        flash('Intern approved and certificate sent successfully!')
    else:
        flash('Intern approved but failed to send certificate email.')
    
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/reject_intern/<int:intern_id>')
@login_required
def reject_intern(intern_id):
    intern = Intern.query.get_or_404(intern_id)
    intern.status = 'rejected'
    db.session.commit()
    flash('Intern rejected successfully!')
    return redirect(url_for('dashboard'))

@app.route('/download_certificate/<int:intern_id>')
@login_required
def download_certificate(intern_id):
    intern = Intern.query.get_or_404(intern_id)
    certificate_buffer = generate_certificate(intern)
    certificate_buffer.seek(0)
    return send_file(
        certificate_buffer,
        as_attachment=True,
        download_name=f"certificate_{intern.name.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True)
