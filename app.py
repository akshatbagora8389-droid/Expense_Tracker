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
from openai import OpenAI

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
# Grok AI configuration (xAI)
# ──────────────────────────────────────────────
grok_client = OpenAI(
    api_key=os.getenv('GROK_API_KEY', ''),
    base_url='https://api.x.ai/v1',
)

# ──────────────────────────────────────────────
# Database helpers
# ──────────────────────────────────────────────

def get_db():
    """Return a new MySQL connection."""
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'expense_tracker'),
    )


def init_db():
    """Create tables if they don't exist (runs on startup)."""
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

    # Build context for Grok
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

    try:
        response = grok_client.chat.completions.create(
            model='grok-3-mini-fast',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
            ],
        )
        reply = response.choices[0].message.content
    except Exception as e:
        app.logger.error(f"Grok API error: {type(e).__name__}: {e}")
        error_str = str(e).lower()
        if '429' in error_str or 'quota' in error_str or 'rate' in error_str:
            reply = ("⚠️ The AI advisor's API rate limit has been reached. "
                     "Please try again later or update the API key in the .env file.")
        else:
            reply = "I'm sorry, I couldn't process your request right now. Please try again later."

    return jsonify({'reply': reply})

# ──────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    debug = os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1', 'yes')
    app.run(debug=debug, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

