import datetime
import hashlib
from Application import db


class User(db.Model):
    def __init__(self, login, email, password, alpha2, public, phone, image):
        self.login = login
        self.email = email
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.alpha2 = alpha2
        self.public = public
        self.phone = phone
        self.image = image

    def check_password(self, password):
        return self.password == hashlib.sha256(password.encode()).hexdigest()

    def update_password(self, password):
        self.password = hashlib.sha256(password.encode()).hexdigest()
        db.session.commit()


    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    alpha2 = db.Column(db.String(2), nullable=False)
    public = db.Column(db.Boolean, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    sessions = db.relationship('Session', backref='user', lazy=True)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    is_open = db.Column(db.Boolean, nullable=False)

    def __init__(self, id, user_id):
        self.id = id
        self.user_id = user_id
        self.is_open = True
        exp = datetime.datetime.now() + datetime.timedelta(days=1)

    def close(self):
        self.is_open = False
        db.session.commit()
