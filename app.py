"""
app.py - Entry point. Creates the Flask app and registers the API routes.
All actual endpoint code lives in routes.py; DB helpers live in db.py.
"""

from flask import Flask
from db import close_db
from routes import api

app = Flask(__name__)
app.register_blueprint(api)
app.teardown_appcontext(close_db)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
