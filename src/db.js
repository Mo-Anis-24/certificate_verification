import sqlite3 from 'sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';
import bcrypt from 'bcrypt';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dbPath = path.join(__dirname, '..', 'data.sqlite');

let db;

export async function initDatabase() {
  sqlite3.verbose();
  db = new sqlite3.Database(dbPath);
  await run(
    'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)'
  );
  await run(
    'CREATE TABLE IF NOT EXISTS certificates (id TEXT PRIMARY KEY, recipient_name TEXT NOT NULL, course_name TEXT NOT NULL, issue_date TEXT NOT NULL, qr_png_data_url TEXT NOT NULL, created_at TEXT NOT NULL)'
  );
}

export function getDb() {
  if (!db) {
    throw new Error('Database not initialized');
  }
  return db;
}

export async function ensureAdminUser() {
  const username = process.env.ADMIN_USERNAME || 'admin';
  const password = process.env.ADMIN_PASSWORD || 'admin123';
  const existing = await get(
    'SELECT id FROM users WHERE username = ? LIMIT 1',
    [username]
  );
  if (!existing) {
    const passwordHash = await bcrypt.hash(password, 10);
    await run('INSERT INTO users (username, password_hash) VALUES (?, ?)', [
      username,
      passwordHash
    ]);
    // eslint-disable-next-line no-console
    console.log(`Seeded admin user: ${username}`);
  }
}

export async function findUserByUsername(username) {
  return await get('SELECT * FROM users WHERE username = ? LIMIT 1', [username]);
}

export async function createCertificate({ id, recipientName, courseName, issueDate, qrCodeDataUrl }) {
  const createdAt = new Date().toISOString();
  await run(
    'INSERT INTO certificates (id, recipient_name, course_name, issue_date, qr_png_data_url, created_at) VALUES (?, ?, ?, ?, ?, ?)',
    [id, recipientName, courseName, issueDate, qrCodeDataUrl, createdAt]
  );
  return await findCertificateById(id);
}

export async function findCertificateById(id) {
  return await get('SELECT * FROM certificates WHERE id = ? LIMIT 1', [id]);
}

// Helper: promisified wrappers
function run(sql, params = []) {
  const database = getDbInstance();
  return new Promise((resolve, reject) => {
    database.run(sql, params, function (err) {
      if (err) return reject(err);
      resolve(this);
    });
  });
}

function get(sql, params = []) {
  const database = getDbInstance();
  return new Promise((resolve, reject) => {
    database.get(sql, params, (err, row) => {
      if (err) return reject(err);
      resolve(row);
    });
  });
}

function getDbInstance() {
  if (!db) {
    db = new sqlite3.Database(dbPath);
  }
  return db;
}