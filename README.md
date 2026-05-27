# 📈 ExpenseIQ — Smart Personal Finance & AI Advisor

ExpenseIQ is a full-stack personal finance application that helps you track every rupee, visualize spending habits, and get personalized financial advice powered by AI. Built with a premium, organic UI and engineered with production-grade security, responsiveness, and resilience.

---

## ✨ Features Highlight

### 🤖 AI Financial Advisor (Resilient & Standardized)
*   **Dual-Provider Intelligence**: Ask anything about your finances and receive custom budgeting tips, savings plans, and spending alerts.
*   **Circuit Breaker & Fallback Protection**: Engineered with a thread-safe health-tracking circuit breaker. If the primary provider (e.g., xAI Grok) experiences issues or exhausts credits, it instantly falls back to Google Gemini within a 5-minute cooldown window, bypassing API hangs.
*   **Optimized Performance**: Completion request timeouts are standardized at a maximum of 10 seconds for rapid, smooth conversations.

### 📱 Responsive Mobile & Collapsible Sidebar
*   **Optimized for iPhone 15 & Safari**: Built to ensure a lag-free 60fps experience on mobile viewports.
*   **No-Lag Performance**: Heavy CSS backdrop-blurs are automatically disabled on mobile in favor of solid hex fills to eliminate layout stuttering.
*   **Zero Tap Latency**: Configured with `-webkit-tap-highlight-color: transparent` and `touch-action: manipulation` to bypass the WebKit click response delay on iOS.
*   **Desktop-Collapsible Sidebar (Slider)**: Click the custom sidebar toggle icon (`dock_to_right`) next to the brand logo inside the sidebar to collapse the menu and expand your workspace. The header toggle button dynamically appears only when the sidebar is closed.

### 🔐 Production-Level Security Hardening
*   **Database Connection Pooling**: Utilizes a robust `MySQLConnectionPool` managing 10 concurrent connections to handle higher traffic volumes.
*   **Leak Protection Guards**: All database operations are wrapped in strictly enforced `try ... finally` statement structures, ensuring connections return to the pool even during queries failures.
*   **Server-Side Inputs Validation**: Validates user registration email patterns, password length (minimum 6 characters), and enforces that transaction amounts are positive numeric inputs.
*   **HTTPS Redirection & HSTS**: Automatically redirects HTTP traffic to HTTPS in production, inspecting `X-Forwarded-Proto` for proxy setups, and enforces Strict-Transport-Security (HSTS).
*   **Cookie Hardening**: Enforces `HttpOnly`, `SameSite=Lax`, and dynamic `Secure` cookie flags on session cookies.
*   **Frame & MIME Protection**: Header filters block clickjacking (`X-Frame-Options: SAMEORIGIN`) and MIME-type sniffing (`X-Content-Type-Options: nosniff`).
*   **Diagnostic Port Shielding**: Protects administrative endpoints; `/api/diagnose` rejects request queries with a `403 Forbidden` unless the Flask server is running in local `debug=True` mode.

### 🎨 Premium Aesthetics & UX Polish
*   **Organic Beige & Green Palette**: Styled with TailwindCSS using HSL-curated color tokens, smooth gradients, and subtle micro-animations.
*   **No-Flicker Navigation**: The landing page navbar uses a transparent border transition trick to resolve WebKit's black-line rendering bug when scrolling back up.
*   **Smooth Scroll Offsets**: The landing page's smooth scroll calculates the sticky header's height dynamically, ensuring navigation jumps don't obscure section titles.
*   **Interactive Visualization**: Renders beautiful expense distribution pie charts and month-on-month trend line graphs powered by `Chart.js`.

---

## 🧪 Comprehensive Automated Testing
The application includes a fully isolated test suite with **40 automated test cases** covering backend routes, database interactions, auth, transaction bounds, and circuit-breaker cooldown limits:
*   [tests/conftest.py](file:///c:/Users/DELL/Desktop/codes/expense-tracker/tests/conftest.py) — Standardized mocks for connection pools.
*   [tests/test_auth.py](file:///c:/Users/DELL/Desktop/codes/expense-tracker/tests/test_auth.py) — Registration, password checks, login/logout, and profile routes.
*   [tests/test_income.py](file:///c:/Users/DELL/Desktop/codes/expense-tracker/tests/test_income.py) & [tests/test_expenses.py](file:///c:/Users/DELL/Desktop/codes/expense-tracker/tests/test_expenses.py) — Bounds checking and categorization filters.
*   [tests/test_advisor.py](file:///c:/Users/DELL/Desktop/codes/expense-tracker/tests/test_advisor.py) — Mocks AI providers and asserts circuit breaker state machine changes.

To run the full test suite locally:
```bash
python -m pytest tests/
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask |
| **Database** | MySQL 8+ (Pooled via MySQLConnectionPool) |
| **Frontend** | Vanilla HTML, TailwindCSS, CSS, Javascript, Chart.js |
| **AI Engine** | xAI Grok-2 API / Google Gemini API (Dual Fallback) |
| **Auth** | bcrypt (password hashing), PyJWT (token sessions), Google OAuth2 |

---

## 🚀 Quick Start (Local Setup)

### 1. Clone & Dependencies
```bash
git clone <your-repo-url>
cd expense-tracker
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Up the MySQL Database
Start your local MySQL server and import the schema:
```bash
mysql -u root -p < db.sql
```

### 3. Configure the Environment
Create your `.env` file from the template:
```bash
cp .env.example .env
```
Edit `.env` and fill in your values:
*   `FLASK_SECRET_KEY`: Generate one using `python -c "import secrets; print(secrets.token_hex(32))"`.
*   `MYSQL_PASSWORD`: Your local MySQL server password.
*   `GEMINI_API_KEY`: Your Google Gemini API key.
*   `DEV_MODE_OAUTH`: Set to `true` to test Google sign-in locally using a simulated developer accounts selection page (no setup needed). Set to `false` to connect real accounts.
*   `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: Your Google Console Web Client credentials (required when `DEV_MODE_OAUTH=false`).

### 4. Run the Dev Server
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000) inside your browser.

---

## 📦 Deployment

### Production WSGI Server
For PaaS hosting (Railway, Render, Heroku), a `Procfile` is pre-configured to run Gunicorn:
```bash
pip install gunicorn
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 2
```

---

## 📂 Project Structure
```
expense-tracker/
├── app.py              # Flask backend (routes, connection pool, API fallback)
├── wsgi.py             # WSGI entry point for production
├── Procfile            # Deployment config for PaaS
├── requirements.txt    # Python dependencies
├── db.sql              # Database schema
├── .env.example        # Environment variable template
├── tests/              # Pytest automated test suite (40 test cases)
└── public/             # Frontend static files
    ├── index.html      # Landing page
    ├── dashboard.html  # Dashboard with Chart.js charts
    ├── income.html     # Income management
    ├── expenses.html   # Expense management
    ├── advisor.html    # AI advisor chat UI
    ├── css/
    │   └── styles.css
    └── js/
        ├── utils.js    # Shared helpers & sidebar event triggers
        ├── auth.js     # Login / signup flows
        ├── advisor.js  # Chat messaging
        └── dashboard.js # Chart.js integrations
```

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
