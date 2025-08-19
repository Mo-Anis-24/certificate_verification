from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from PIL import Image
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interns.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Config (suggestion: move to environment variables later)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pvariya807@gmail.com'
app.config['MAIL_PASSWORD'] = 'vrso zdmg hkci xlhb'

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
    subject = db.Column(db.String(100), nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')
    certificate_sent = db.Column(db.Boolean, default=False)
    verification_id = db.Column(db.String(50), unique=True)

class Trainee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(140), nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')
    certificate_sent = db.Column(db.Boolean, default=False)
    verification_id = db.Column(db.String(50), unique=True)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# -------- Certificate Generator (ALL TEXT REMOVED) --------
def generate_certificate(intern):
    """
    Generate a certificate PDF by drawing the intern's name and details
    onto the certificate template image.
    """
    template_path = os.path.join('static', 'demoooooo.png')

    # Load template to get dimensions
    template_image = Image.open(template_path).convert("RGB")
    img_width, img_height = template_image.size

    # Prepare PDF canvas with the same dimensions as the template image
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=(img_width, img_height))

    # Draw the template image as background
    pdf.drawImage(ImageReader(template_image), 0, 0, width=img_width, height=img_height)

    # Helper: ordinal date like 29th June 2024
    def to_ordinal(n):
        if 10 <= n % 100 <= 20:
            return f"{n}th"
        return f"{n}{['th','st','nd','rd','th','th','th','th','th','th'][n % 10]}"

    def format_date_with_ordinal(d):
        return f"{to_ordinal(d.day)} {d.strftime('%B %Y')}"

    # Build three lines for internship or training completion
    subject_text = getattr(intern, 'subject', None) or getattr(intern, 'course', '')
    start_text = format_date_with_ordinal(intern.joining_date)
    end_text = format_date_with_ordinal(intern.end_date)
    is_trainee = hasattr(intern, 'course') and not hasattr(intern, 'subject')
    line1 = "for successfully completing the"
    if is_trainee:
        # Trainee certificate wording (training completion)
        line2 = f"Broaderai Training Program in {subject_text} hosted from"
    else:
        # Intern certificate wording (internship completion)
        line2 = f"Broaderai Internship Program for 2 credits with {subject_text} hosted from"
    line3 = f"{start_text} to {end_text}"

    # Text styling
    name_font = "Helvetica-Bold"
    name_size = 60
    body_font = "Helvetica"
    base_body_size = 30
    text_color_rgb = (0, 0, 0)

    pdf.setFillColorRGB(*text_color_rgb)

    # Center helper
    def draw_centered(text: str, y: float, font_name: str, font_size: int):
        pdf.setFont(font_name, font_size)
        pdf.drawCentredString(img_width / 1.8 + 50, y, text)

    # Fit helper: reduce font size until line fits max width
    def fit_font_size_for_line(text: str, font_name: str, starting_size: int, max_width: float, min_size: int = 16) -> int:
        size = starting_size
        while size > min_size and pdf.stringWidth(text, font_name, size) > max_width:
            size -= 1
        return size

    # Fit helper: ensure all lines share the same size and fit the width
    def fit_font_size_for_all(lines, font_name: str, starting_size: int, max_width: float, min_size: int = 16) -> int:
        size = starting_size
        while size > min_size:
            if all(pdf.stringWidth(line, font_name, size) <= max_width for line in lines):
                break
            size -= 1
        return size

    # Positions (relative to image height); tuned to appear under the pre-printed heading
    name_y = img_height * 0.56
    body_y_start = img_height * 0.48
    max_text_width = img_width * 0.80

    # Draw intern name
    name_size = fit_font_size_for_line(intern.name, name_font, name_size, max_text_width)
    draw_centered(intern.name, name_y, name_font, name_size)

    # Draw underline beneath the name, centered with the same horizontal offset
    name_text_width = pdf.stringWidth(intern.name, name_font, name_size)
    center_x = img_width / 1.8 + 50
    underline_length = min(name_text_width + 40, max_text_width)
    underline_y = name_y - name_size * 0.25
    pdf.setStrokeColorRGB(*text_color_rgb)
    pdf.setLineWidth(2)
    pdf.line(center_x - underline_length / 2, underline_y, center_x + underline_length / 2, underline_y)

    # Draw three centered lines beneath the name (uniform size)
    uniform_body_size = fit_font_size_for_all([line1, line2, line3], body_font, base_body_size, max_text_width)
    line_spacing = uniform_body_size * 1.35
    current_y = body_y_start
    draw_centered(line1, current_y, body_font, uniform_body_size)
    current_y -= line_spacing
    draw_centered(line2, current_y, body_font, uniform_body_size)
    current_y -= line_spacing
    draw_centered(line3, current_y, body_font, uniform_body_size)

    # Add a goodwill message line below with a small gap
    current_y -= line_spacing * 1.2
    wish_text = "We wish you good luck for all your future endeavours"
    wish_size = fit_font_size_for_line(wish_text, body_font, uniform_body_size, max_text_width)
    draw_centered(wish_text, current_y, body_font, wish_size)

    # Optionally add verification id if present (small footer text)
    # Add clickable verification URL above founder area
    try:
        verify_url = url_for('index', _external=True)
    except Exception:
        verify_url = '/'
    url_center_x = img_width / 1.9 - 10  # moved further left
    link_text = f"Verify at: {verify_url}"
    link_font_size = min(
        uniform_body_size,
        fit_font_size_for_line(link_text, body_font, uniform_body_size, max_text_width)
    )
    url_y = img_height * 0.10  # moved further down near the line
    pdf.setFont(body_font, link_font_size)
    pdf.drawCentredString(url_center_x, url_y, link_text)
    text_width = pdf.stringWidth(link_text, body_font, link_font_size)
    pdf.linkURL(
        verify_url,
        (
            url_center_x - text_width / 2,
            url_y - 2,
            url_center_x + text_width / 2,
            url_y + link_font_size + 2,
        ),
        relative=0,
    )

    # Draw Verification ID at top-right corner
    if intern.verification_id:
        id_text = f"Verification ID: {intern.verification_id}"
        id_font_size = min(
            uniform_body_size,
            fit_font_size_for_line(id_text, body_font, uniform_body_size, max_text_width)
        )
        right_margin = img_width * 0.04
        id_y = img_height * 0.92
        pdf.setFont(body_font, id_font_size)
        id_text_width = pdf.stringWidth(id_text, body_font, id_font_size)
        pdf.drawString(img_width - right_margin - id_text_width, id_y, id_text)

    pdf.showPage()
    pdf.save()
    output.seek(0)
    return output
# ----------------------------------------------------------

def send_certificate_email(intern, certificate_buffer):
    try:
        msg = Message(
            subject='BROADER AI - Your Internship Certificate',
            sender=app.config['MAIL_USERNAME'],
            recipients=[intern.email]
        )
        msg.body = f"""
Dear {intern.name},

Congratulations! Your internship at BROADER AI has been successfully completed and approved.

Your certificate is attached to this email.
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
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('choose_panel'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/choose_panel')
@login_required
def choose_panel():
    return render_template('choose_panel.html')

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
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        subject = request.form['subject'].strip()
        joining_date = datetime.strptime(request.form['joining_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        
        intern = Intern(
            name=name,
            email=email,
            subject=subject,
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
    if not intern.verification_id:
        intern.verification_id = str(uuid.uuid4())[:8].upper()
    certificate_buffer = generate_certificate(intern)
    if send_certificate_email(intern, certificate_buffer):
        intern.certificate_sent = True
        flash('Intern approved and certificate sent successfully!')
    else:
        flash('Intern approved but failed to send certificate email.')
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/trainees')
@login_required
def trainees_dashboard():
    trainees = Trainee.query.all()
    return render_template('trainees_dashboard.html', trainees=trainees)

@app.route('/add_trainee', methods=['GET', 'POST'])
@login_required
def add_trainee():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        course = request.form['course'].strip()
        joining_date = datetime.strptime(request.form['joining_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        trainee = Trainee(
            name=name,
            email=email,
            course=course,
            joining_date=joining_date,
            end_date=end_date
        )
        db.session.add(trainee)
        db.session.commit()
        flash('Trainee added successfully!')
        return redirect(url_for('trainees_dashboard'))
    return render_template('add_trainee.html')

@app.route('/approve_trainee/<int:trainee_id>')
@login_required
def approve_trainee(trainee_id):
    trainee = Trainee.query.get_or_404(trainee_id)
    trainee.status = 'approved'
    if not trainee.verification_id:
        trainee.verification_id = str(uuid.uuid4())[:8].upper()
    certificate_buffer = generate_certificate(trainee)
    if send_certificate_email(trainee, certificate_buffer):
        trainee.certificate_sent = True
        flash('Trainee approved and certificate sent successfully!')
    else:
        flash('Trainee approved but failed to send certificate email.')
    db.session.commit()
    return redirect(url_for('trainees_dashboard'))

@app.route('/reject_trainee/<int:trainee_id>')
@login_required
def reject_trainee(trainee_id):
    trainee = Trainee.query.get_or_404(trainee_id)
    trainee.status = 'rejected'
    db.session.commit()
    flash('Trainee rejected successfully!')
    return redirect(url_for('trainees_dashboard'))

@app.route('/download_trainee_certificate/<int:trainee_id>')
@login_required
def download_trainee_certificate(trainee_id):
    trainee = Trainee.query.get_or_404(trainee_id)
    if not trainee.verification_id:
        trainee.verification_id = str(uuid.uuid4())[:8].upper()
        db.session.commit()
    certificate_buffer = generate_certificate(trainee)
    certificate_buffer.seek(0)
    return send_file(
        certificate_buffer,
        as_attachment=True,
        download_name=f"certificate_{trainee.name.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

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
    if not intern.verification_id:
        intern.verification_id = str(uuid.uuid4())[:8].upper()
        db.session.commit()
    certificate_buffer = generate_certificate(intern)
    certificate_buffer.seek(0)
    return send_file(
        certificate_buffer,
        as_attachment=True,
        download_name=f"certificate_{intern.name.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    details = None
    if request.method == 'POST':
        vid = request.form['verification_id'].strip().upper()
        details = Intern.query.filter_by(verification_id=vid).first()
        if not details:
            details = Trainee.query.filter_by(verification_id=vid).first()
        return render_template('home.html', details=details)
    # GET: redirect to home to use the on-page verification form
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
