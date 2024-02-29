import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .db_countries import Countries

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRES_CONN")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
countries = Countries()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from Application import routes_app, models, login
