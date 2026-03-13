"""WSGI entry point for production deployment."""
from app import app, init_db

# Ensure tables exist on startup
init_db()

if __name__ == '__main__':
    app.run()
