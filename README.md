# ExpenseIQ — Smart Expense Tracker

A full-stack expense tracking application with AI-powered financial advice, built with **Flask**, **MySQL**, and **vanilla HTML/CSS/JS**.

## Features

- 🎨 **Warm Beige & Green Theme** — Polished, premium minimalism with organic color-coded badges and custom SVG icons (no generic emojis)
- 📊 **Dashboard** — Beautiful pie charts and line graphs styled in organic tones for clear spending insights
- 💰 **Income Management** — Track and manage all your income sources
- 💸 **Expense Tracking** — Categorize and track all spending dynamically
- 🤖 **AI Financial Advisor** — Get personalized budgeting tips powered by Google Gemini
- 🔐 **Secure Auth & Google Login** — Traditional bcrypt email login plus **Google Sign In** integration
- 🧪 **Developer OAuth Mock Mode** — Simulated developer authorization screen to test login/signup flows locally without API keys

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask |
| Database | MySQL 8+ |
| Frontend | HTML, CSS, JavaScript (Chart.js) |
| AI | Google Gemini API |
| Auth | bcrypt, PyJWT, Google OAuth2 |

## Quick Start (Local)

### 1. Clone & Install

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

### 2. Set Up the Database

Make sure MySQL is running, then:

```bash
mysql -u root -p < db.sql
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:
- `FLASK_SECRET_KEY` — Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `MYSQL_PASSWORD` — Your MySQL root password
- `GEMINI_API_KEY` — Your Google Gemini API key
- `DEV_MODE_OAUTH` — Set to `true` to test Google sign-in locally using a simulated developer accounts selection page (no setup needed). Set to `false` to connect real accounts.
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — Your Google Console Web Client credentials (required when `DEV_MODE_OAUTH=false`)

### 4. Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

## Production Deployment

### Using Gunicorn (Heroku / Render / Railway)

The project includes a `Procfile` and `wsgi.py` for one-click deployment:

```bash
# Install production server
pip install gunicorn

# Run locally with Gunicorn
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 2
```

### Environment Variables

Set all variables from `.env.example` in your platform's dashboard. **Important:**
- Set `FLASK_SECRET_KEY` to a strong random value
- Set `FLASK_DEBUG` to `false`
- Point `MYSQL_*` variables to your cloud MySQL instance

### Recommended Platforms

| Platform | Database Option |
|---|---|
| [Render](https://render.com) | Add a MySQL add-on or use PlanetScale |
| [Railway](https://railway.app) | Built-in MySQL plugin |
| [Heroku](https://heroku.com) | JawsDB or ClearDB add-on |

## Project Structure

```
expense-tracker/
├── app.py              # Flask backend (routes, API, config)
├── wsgi.py             # WSGI entry point for production
├── Procfile            # Deployment config for PaaS
├── requirements.txt    # Python dependencies
├── db.sql              # Database schema
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── public/             # Frontend static files
    ├── index.html      # Landing page
    ├── dashboard.html  # Dashboard with charts
    ├── income.html     # Income management
    ├── expenses.html   # Expense management
    ├── advisor.html    # AI advisor chat
    ├── css/
    │   └── styles.css
    └── js/
        ├── auth.js
        ├── dashboard.js
        ├── income.js
        ├── expenses.js
        └── advisor.js
```

## License

MIT
