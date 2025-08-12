import express from 'express';
import session from 'express-session';
import path from 'path';
import { fileURLToPath } from 'url';
import QRCode from 'qrcode';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import { initDatabase, getDb, ensureAdminUser, findUserByUsername, createCertificate, findCertificateById } from './src/db.js';
import bcrypt from 'bcrypt';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(
  session({
    secret: process.env.SESSION_SECRET || 'devsessionsecret',
    resave: false,
    saveUninitialized: false,
    cookie: { httpOnly: true, sameSite: 'lax' }
  })
);

app.use(express.static(path.join(__dirname, 'public')));

// Initialize DB and seed admin
await initDatabase();
await ensureAdminUser();

function requireAuth(req, res, next) {
  if (!req.session || !req.session.userId) {
    return res.status(401).send('Unauthorized. Please log in.');
  }
  next();
}

// Auth routes
app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password are required' });
  }
  try {
    const user = await findUserByUsername(username);
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    const passwordMatches = await bcrypt.compare(password, user.password_hash);
    if (!passwordMatches) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    req.session.userId = user.id;
    req.session.username = user.username;
    return res.json({ success: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/logout', (req, res) => {
  req.session.destroy(() => {
    res.json({ success: true });
  });
});

// Admin dashboard (protected)
app.get('/admin/dashboard', requireAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'admin-dashboard.html'));
});

// Create a certificate (protected)
app.post('/api/certificates', requireAuth, async (req, res) => {
  const { recipientName, courseName, issueDate } = req.body;
  if (!recipientName || !courseName) {
    return res.status(400).json({ error: 'recipientName and courseName are required' });
  }
  try {
    const certificateId = uuidv4();
    const verifyUrl = `${req.protocol}://${req.get('host')}/verify?id=${encodeURIComponent(certificateId)}`;
    const qrCodeDataUrl = await QRCode.toDataURL(verifyUrl, { width: 300, margin: 1 });

    const certificate = await createCertificate({
      id: certificateId,
      recipientName,
      courseName,
      issueDate: issueDate || new Date().toISOString().slice(0, 10),
      qrCodeDataUrl
    });

    return res.json({ success: true, certificate });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Failed to create certificate' });
  }
});

// Verify certificate - HTML view if id present, otherwise serve verify page
app.get('/verify', async (req, res) => {
  const { id } = req.query;
  if (!id) {
    return res.sendFile(path.join(__dirname, 'public', 'verify.html'));
  }
  try {
    const cert = await findCertificateById(id);
    if (!cert) {
      return res.status(404).sendFile(path.join(__dirname, 'public', 'verify-not-found.html'));
    }
    // Render a simple HTML result
    const verifyUrl = `${req.protocol}://${req.get('host')}/verify?id=${encodeURIComponent(id)}`;
    const html = `
      <!doctype html>
      <html>
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Certificate Verification</title>
          <link rel="stylesheet" href="/styles.css" />
        </head>
        <body>
          <div class="container">
            <h1>Certificate is Valid ✅</h1>
            <div class="card">
              <p><strong>Certificate ID:</strong> ${cert.id}</p>
              <p><strong>Recipient:</strong> ${cert.recipient_name}</p>
              <p><strong>Course:</strong> ${cert.course_name}</p>
              <p><strong>Issued On:</strong> ${cert.issue_date}</p>
              <img src="${cert.qr_png_data_url}" alt="QR Code" style="max-width: 200px;" />
              <p><a href="${verifyUrl}">Share verification link</a></p>
            </div>
            <p><a href="/">Back to Home</a></p>
          </div>
        </body>
      </html>
    `;
    res.send(html);
  } catch (err) {
    console.error(err);
    return res.status(500).send('Server error');
  }
});

// Verification API for form-based verification
app.get('/api/verify/:id', async (req, res) => {
  try {
    const cert = await findCertificateById(req.params.id);
    if (!cert) {
      return res.status(404).json({ valid: false });
    }
    return res.json({
      valid: true,
      certificate: {
        id: cert.id,
        recipientName: cert.recipient_name,
        courseName: cert.course_name,
        issueDate: cert.issue_date,
        qrCodeDataUrl: cert.qr_png_data_url
      }
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Server error' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});