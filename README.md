# ExpenseIQ — Smart Expense Tracker

A full-stack expense tracking application with AI-powered financial advice, built with **Flask**, **MySQL**, and **vanilla HTML/CSS/JS**.

## Features

- 📊 **Dashboard** — Summary cards, pie charts, and line graphs for spending insights
- 💰 **Income Management** — Add, view, and delete income entries
- 💸 **Expense Tracking** — Categorise and track spending
- 🤖 **AI Financial Advisor** — Personalised advice powered by Google Gemini
- 🔐 **User Authentication** — Secure login/register with bcrypt

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask |
| Database | MySQL 8+ |
| Frontend | HTML, CSS, JavaScript |
| AI | Google Gemini API |
| Auth | bcrypt + Flask sessions |

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
