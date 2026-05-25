import os
import logging
import functools
from datetime import datetime, date
from decimal import Decimal

from flask import (
    Flask, request, jsonify, session, redirect, url_for, send_from_directory
)
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector
import bcrypt
import google.generativeai as genai

load_dotenv()

# ──────────────────────────────────────────────
# App Configuration
# ──────────────────────────────────────────────

app = Flask(__name__, static_folder='public', static_url_path='')

# Secret key — MUST be set via env in production
secret_key = os.getenv('FLASK_SECRET_KEY')
if not secret_key or secret_key == 'change-me':
    import secrets
    secret_key = secrets.token_hex(32)
    app.logger.warning(
        'FLASK_SECRET_KEY not set — using a random key. '
        'Sessions will NOT persist across restarts. '
        'Set FLASK_SECRET_KEY in your .env or environment variables.'
    )
app.secret_key = secret_key

# CORS — allow all origins in dev, restrict in production if needed
CORS(app, supports_credentials=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

# ──────────────────────────────────────────────
# Google Generative AI (Gemini) configuration
# ──────────────────────────────────────────────
gemini_api_key = os.getenv('GEMINI_API_KEY', '')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
# We handle missing keys gracefully in the route below.

# ──────────────────────────────────────────────
# Database helpers
# ──────────────────────────────────────────────

import time

def get_db():
    """Return a new MySQL connection, supporting both standard and Railway environment variables."""
    host = os.getenv('MYSQL_HOST') or os.getenv('MYSQLHOST') or 'localhost'
    
    port_str = os.getenv('MYSQL_PORT') or os.getenv('MYSQLPORT') or '3306'
    try:
        port = int(port_str)
    except ValueError:
        port = 3306
        
    user = os.getenv('MYSQL_USER') or os.getenv('MYSQLUSER') or 'root'
    password = os.getenv('MYSQL_PASSWORD') or os.getenv('MYSQLPASSWORD') or ''
    database = os.getenv('MYSQL_DATABASE') or os.getenv('MYSQLDATABASE') or 'expense_tracker'
    
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )


def init_db():
    """Create tables if they don't exist (runs on startup). Retries on failure to handle database boot times."""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f"INFO: Connecting to MySQL database (attempt {attempt + 1}/{max_retries})...")
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS income (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    source VARCHAR(100) NOT NULL,
                    amount DECIMAL(12,2) NOT NULL,
                    date DATE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    amount DECIMAL(12,2) NOT NULL,
                    date DATE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("INFO: Database initialized successfully.")
            return
        except Exception as e:
            print(f"WARNING: Database connection failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                print("CRITICAL: Could not connect to database after maximum retries. Starting Flask application anyway (subsequent queries will retry dynamically).")


# JSON serializer helper
def _serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


def rows_to_dicts(cursor):
    columns = [desc[0] for desc in cursor.description]
    return [
        {col: _serialize(val) for col, val in zip(columns, row)}
        for row in cursor.fetchall()
    ]

# ──────────────────────────────────────────────
# Global Error Handler
# ──────────────────────────────────────────────

@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler to return JSON instead of HTML for backend crashes."""
    app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(e)
    }), 500


# ──────────────────────────────────────────────
# Auth middleware
# ──────────────────────────────────────────────

def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper

# ──────────────────────────────────────────────
# Static pages
# ──────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/dashboard')
def dashboard_page():
    return send_from_directory('public', 'dashboard.html')


@app.route('/income-page')
def income_page():
    return send_from_directory('public', 'income.html')


@app.route('/expenses-page')
def expenses_page():
    return send_from_directory('public', 'expenses.html')


@app.route('/advisor-page')
def advisor_page():
    return send_from_directory('public', 'advisor.html')

# ──────────────────────────────────────────────
# Auth API
# ──────────────────────────────────────────────

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
            (username, email, pw_hash),
        )
        conn.commit()
        user_id = cur.lastrowid
        cur.close()
        conn.close()
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Username or email already exists'}), 409

    session['user_id'] = user_id
    session['username'] = username
    return jsonify({'message': 'Registered successfully', 'username': username}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username, password_hash FROM users WHERE email = %s', (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return jsonify({'error': 'Invalid credentials'}), 401

    user_id, username, pw_hash = row
    if not bcrypt.checkpw(password.encode(), pw_hash.encode()):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['user_id'] = user_id
    session['username'] = username
    return jsonify({'message': 'Login successful', 'username': username})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})


@app.route('/api/auth/me')
def me():
    if 'user_id' not in session:
        return jsonify({'logged_in': False}), 401
    return jsonify({'logged_in': True, 'username': session['username'], 'user_id': session['user_id']})

# ──────────────────────────────────────────────
# Income API
# ──────────────────────────────────────────────

@app.route('/api/income', methods=['GET'])
@login_required
def get_income():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'SELECT id, source, amount, date, description, created_at FROM income WHERE user_id = %s ORDER BY date DESC',
        (session['user_id'],),
    )
    data = rows_to_dicts(cur)
    cur.close()
    conn.close()
    return jsonify(data)


@app.route('/api/income', methods=['POST'])
@login_required
def add_income():
    data = request.get_json()
    source = data.get('source', '').strip()
    amount = data.get('amount')
    inc_date = data.get('date')
    description = data.get('description', '').strip()

    if not source or not amount or not inc_date:
        return jsonify({'error': 'Source, amount, and date are required'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO income (user_id, source, amount, date, description) VALUES (%s, %s, %s, %s, %s)',
        (session['user_id'], source, amount, inc_date, description),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({'message': 'Income added', 'id': new_id}), 201


@app.route('/api/income/<int:income_id>', methods=['DELETE'])
@login_required
def delete_income(income_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM income WHERE id = %s AND user_id = %s', (income_id, session['user_id']))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    if affected == 0:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'message': 'Deleted'})

# ──────────────────────────────────────────────
# Expenses API
# ──────────────────────────────────────────────

@app.route('/api/expenses', methods=['GET'])
@login_required
def get_expenses():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'SELECT id, category, amount, date, description, created_at FROM expenses WHERE user_id = %s ORDER BY date DESC',
        (session['user_id'],),
    )
    data = rows_to_dicts(cur)
    cur.close()
    conn.close()
    return jsonify(data)


@app.route('/api/expenses', methods=['POST'])
@login_required
def add_expense():
    data = request.get_json()
    category = data.get('category', '').strip()
    amount = data.get('amount')
    exp_date = data.get('date')
    description = data.get('description', '').strip()

    if not category or not amount or not exp_date:
        return jsonify({'error': 'Category, amount, and date are required'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO expenses (user_id, category, amount, date, description) VALUES (%s, %s, %s, %s, %s)',
        (session['user_id'], category, amount, exp_date, description),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({'message': 'Expense added', 'id': new_id}), 201


@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM expenses WHERE id = %s AND user_id = %s', (expense_id, session['user_id']))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    if affected == 0:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'message': 'Deleted'})

# ──────────────────────────────────────────────
# Dashboard API
# ──────────────────────────────────────────────

@app.route('/api/dashboard/summary')
@login_required
def dashboard_summary():
    uid = session['user_id']
    conn = get_db()
    cur = conn.cursor()

    # Total income
    cur.execute('SELECT COALESCE(SUM(amount), 0) FROM income WHERE user_id = %s', (uid,))
    total_income = float(cur.fetchone()[0])

    # Total expenses
    cur.execute('SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = %s', (uid,))
    total_expenses = float(cur.fetchone()[0])

    # Income by source (for pie chart)
    cur.execute(
        'SELECT source, SUM(amount) as total FROM income WHERE user_id = %s GROUP BY source ORDER BY total DESC',
        (uid,),
    )
    income_by_source = [{'source': r[0], 'total': float(r[1])} for r in cur.fetchall()]

    # Expenses over time (for line chart) — grouped by month
    cur.execute(
        """SELECT CONCAT(YEAR(date), '-', LPAD(MONTH(date), 2, '0')) as month, SUM(amount) as total
           FROM expenses WHERE user_id = %s
           GROUP BY month ORDER BY month ASC""",
        (uid,),
    )
    expenses_over_time = [{'month': r[0], 'total': float(r[1])} for r in cur.fetchall()]

    # Recent transactions (last 5 of each)
    cur.execute(
        "SELECT 'income' as type, source as label, amount, date FROM income WHERE user_id = %s "
        "UNION ALL "
        "SELECT 'expense' as type, category as label, amount, date FROM expenses WHERE user_id = %s "
        "ORDER BY date DESC LIMIT 10",
        (uid, uid),
    )
    recent = rows_to_dicts(cur)

    cur.close()
    conn.close()

    return jsonify({
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': total_income - total_expenses,
        'income_by_source': income_by_source,
        'expenses_over_time': expenses_over_time,
        'recent_transactions': recent,
    })

# ──────────────────────────────────────────────
# AI Chat API
# ──────────────────────────────────────────────

@app.route('/api/chat', methods=['POST'])
@login_required
def ai_chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    uid = session['user_id']
    conn = get_db()
    cur = conn.cursor()

    # Gather financial context
    cur.execute('SELECT COALESCE(SUM(amount), 0) FROM income WHERE user_id = %s', (uid,))
    total_income = float(cur.fetchone()[0])

    cur.execute('SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = %s', (uid,))
    total_expenses = float(cur.fetchone()[0])

    balance = total_income - total_expenses

    # Income breakdown
    cur.execute(
        'SELECT source, SUM(amount) as total FROM income WHERE user_id = %s GROUP BY source ORDER BY total DESC',
        (uid,),
    )
    income_sources = [{'source': r[0], 'total': float(r[1])} for r in cur.fetchall()]

    # Expense breakdown by category
    cur.execute(
        'SELECT category, SUM(amount) as total FROM expenses WHERE user_id = %s GROUP BY category ORDER BY total DESC',
        (uid,),
    )
    expense_categories = [{'category': r[0], 'total': float(r[1])} for r in cur.fetchall()]

    # Recent transactions
    cur.execute(
        "SELECT 'income' as type, source as label, amount, date FROM income WHERE user_id = %s "
        "UNION ALL "
        "SELECT 'expense' as type, category as label, amount, date FROM expenses WHERE user_id = %s "
        "ORDER BY date DESC LIMIT 15",
        (uid, uid),
    )
    recent = rows_to_dicts(cur)

    cur.close()
    conn.close()

    # Build context for Gemini
    financial_context = (
        f"User's Financial Summary:\n"
        f"- Total Income: ₹{total_income:,.2f}\n"
        f"- Total Expenses: ₹{total_expenses:,.2f}\n"
        f"- Current Balance: ₹{balance:,.2f}\n\n"
        f"Income Sources: {income_sources}\n"
        f"Expense Categories: {expense_categories}\n"
        f"Recent Transactions: {recent}\n"
    )

    system_prompt = (
        "You are ExpenseIQ's AI Financial Advisor — a friendly, knowledgeable personal finance assistant. "
        "You have access to the user's real financial data shown below. "
        "Use this data to give personalized, actionable advice. "
        "When the user asks about purchasing decisions, evaluate whether they can afford it based on their balance and spending patterns. "
        "Suggest savings strategies, budgeting tips, and smart financial decisions. "
        "Keep responses concise, warm, and practical. Use bullet points and bold text for clarity. "
        "Always reference the user's actual numbers when relevant. "
        "If the user's balance is low, gently warn them. "
        "Currency is Indian Rupees (₹).\n\n"
        f"{financial_context}"
    )
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        return jsonify({'reply': "⚠️ The Gemini API key is missing. Please set GEMINI_API_KEY in the .env file."})

    try:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
        response = model.generate_content(user_message)
        reply = response.text
    except Exception as e:
        app.logger.error(f"Gemini API error: {type(e).__name__}: {e}")
        error_str = str(e).lower()
        if '429' in error_str or 'quota' in error_str or 'rate' in error_str:
            reply = ("⚠️ The AI advisor's API rate limit has been reached. "
                     "Please try again later or update the API key in the .env file.")
        else:
            reply = "I'm sorry, I couldn't process your request right now. Please try again later."

    return jsonify({'reply': reply})

# ──────────────────────────────────────────────
# Google & Apple Authentication Routes
# ──────────────────────────────────────────────

import uuid
import urllib.parse
import requests

def is_oauth_dev_mode():
    return os.getenv('DEV_MODE_OAUTH', 'false').lower() in ('true', '1', 'yes')


def login_or_register_social_user(email, username):
    if not email:
        return False
        
    conn = get_db()
    cur = conn.cursor()
    try:
        # Check if user exists by email
        cur.execute("SELECT id, username FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            user_id, existing_username = user
            session['user_id'] = user_id
            session['username'] = existing_username
            return True
        else:
            # User doesn't exist, create them
            base_username = username or email.split('@')[0]
            # Clean base username
            base_username = ''.join(c for c in base_username if c.isalnum() or c in '._-')
            if not base_username:
                base_username = "user"
                
            # Ensure unique username
            cur.execute("SELECT id FROM users WHERE username = %s", (base_username,))
            if cur.fetchone():
                base_username = f"{base_username}_{str(uuid.uuid4())[:6]}"
            
            # Generate dummy password hash for security
            dummy_pwd = uuid.uuid4().hex
            pwd_hash = bcrypt.hashpw(dummy_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (base_username, email, pwd_hash)
            )
            conn.commit()
            new_user_id = cur.lastrowid
            session['user_id'] = new_user_id
            session['username'] = base_username
            return True
    except Exception as e:
        app.logger.error(f"Social authentication DB error: {e}")
        return False
    finally:
        cur.close()
        conn.close()


# --- Google OAuth Routes ---

@app.route('/api/auth/google')
def google_login():
    if is_oauth_dev_mode():
        return redirect('/api/auth/mock/google')
        
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    google_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        "scope=openid%20email%20profile"
    )
    return redirect(google_url)


@app.route('/api/auth/google/callback')
def google_callback():
    code = request.args.get('code')
    if not code:
        return redirect('/?error=no_auth_code')
        
    # Handle local dev mock login
    if is_oauth_dev_mode() and code.startswith('mock-'):
        email = "test_google@example.com" if "testuser" in code else "new_google@example.com"
        name = "Test Google User" if "testuser" in code else "New Google User"
        if login_or_register_social_user(email, name):
            return redirect('/dashboard')
        else:
            return redirect('/?error=social_db_failed')

    # Real Google OAuth exchange
    try:
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        r = requests.post(token_url, data=data)
        if r.status_code != 200:
            app.logger.error(f"Google token exchange failed: {r.text}")
            return redirect('/?error=google_token_failed')
            
        tokens = r.json()
        access_token = tokens.get('access_token')
        
        # Get user details
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        r_user = requests.get(userinfo_url, headers=headers)
        if r_user.status_code != 200:
            return redirect('/?error=google_userinfo_failed')
            
        user_data = r_user.json()
        email = user_data.get('email')
        name = user_data.get('name')
        
        if login_or_register_social_user(email, name):
            return redirect('/dashboard')
        else:
            return redirect('/?error=social_db_failed')
    except Exception as e:
        app.logger.error(f"Google OAuth Exception: {e}")
        return redirect('/?error=google_oauth_exception')


# --- Apple Sign In Routes Removed ---


# --- Developer Mock OAuth Screens ---

@app.route('/api/auth/mock/google')
def mock_google_auth():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign in - Google Accounts</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
                background-color: #FAF8F5;
                color: #2C2520;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
            }
            .card {
                background: #FFFFFF;
                border: 1px solid rgba(44, 37, 32, 0.08);
                border-radius: 20px;
                padding: 44px 40px;
                width: 100%;
                max-width: 380px;
                box-shadow: 0 12px 40px rgba(44, 37, 32, 0.04);
                text-align: center;
            }
            .logo {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                font-size: 1.6rem;
                font-weight: 800;
                margin-bottom: 28px;
                letter-spacing: -0.02em;
            }
            .logo span:nth-child(1) { color: #4285F4; }
            .logo span:nth-child(2) { color: #EA4335; }
            .logo span:nth-child(3) { color: #FBBC05; }
            .logo span:nth-child(4) { color: #34A853; }
            h2 {
                font-size: 1.35rem;
                font-weight: 700;
                margin-bottom: 8px;
                letter-spacing: -0.02em;
            }
            p {
                color: #70655C;
                font-size: 0.92rem;
                margin-bottom: 32px;
                line-height: 1.5;
            }
            .account-btn {
                display: block;
                width: 100%;
                padding: 16px;
                margin-bottom: 14px;
                background: #FAF8F5;
                border: 1px solid rgba(44, 37, 32, 0.08);
                border-radius: 12px;
                text-align: left;
                cursor: pointer;
                font-family: inherit;
                font-weight: 700;
                color: #2C2520;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .account-btn:hover {
                background: #F3ECE2;
                border-color: rgba(44, 37, 32, 0.15);
                transform: translateY(-1px);
            }
            .account-email {
                font-size: 0.82rem;
                color: #70655C;
                font-weight: 500;
                display: block;
                margin-top: 3px;
            }
            .footer-info {
                font-size: 0.76rem;
                color: #968B80;
                margin-top: 32px;
                line-height: 1.4;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="logo">
                <span>G</span><span>o</span><span>o</span><span>g</span><span>l</span><span>e</span>
            </div>
            <h2>Choose an account</h2>
            <p>to continue to <strong>ExpenseIQ</strong></p>
            
            <button class="account-btn" onclick="select('mock-google-code-testuser')">
                Test Google User
                <span class="account-email">test_google@example.com</span>
            </button>
            <button class="account-btn" onclick="select('mock-google-code-newuser')">
                New Google User
                <span class="account-email">new_google@example.com</span>
            </button>
            <div class="footer-info">
                This is a secure developer mock authorization screen. No password is required.
            </div>
        </div>
        <script>
            function select(code) {
                window.location.href = '/api/auth/google/callback?code=' + code;
            }
        </script>
    </body>
    </html>
    """


# --- Apple Mock Auth Removed ---

# ──────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    debug = os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1', 'yes')
    app.run(debug=debug, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

