import datetime
import hashlib
from application import db
import re


class User(db.Model):
    def __init__(self, login, email, password, alpha2, public, phone=None, image=None):
        self.login = login
        self.email = email
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.alpha2 = alpha2
        self.public = public
        self.phone = phone
        self.image = image

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def match_passwords(self, password):
        return self.password == hashlib.sha256(password.encode()).hexdigest()

    def update_password(self, password):
        self.password = hashlib.sha256(password.encode()).hexdigest()
        for session in self.sessions:
            db.session.delete(session)
        db.session.commit()

    def get_info(self):
        response = {
            "login": self.login,
            "email": self.email,
            "countryCode": self.alpha2,
            "isPublic": self.public,
        }
        if self.phone is not None:
            response["phone"] = self.phone
        if self.image is not None:
            response["image"] = self.image
        return response

    def get_id(self):
        return self.id

    @staticmethod
    def check_email(email):  # check if email is unique and correct
        if email is None:
            return 'Email is empty', 400
        if len(email) > 50:
            return 'Email is too long', 400
        rows = User.query.filter_by(email=email).all()
        if len(rows) > 0:
            return 'Email already exists', 409
        else:
            return 'OK', 200

    @staticmethod
    def check_password(password):  # check if password is correct
        if password is None:
            return 'Password is empty', 400
        if len(password) > 100:
            return 'Password is too long', 400
        if len(password) < 6:
            return 'Password is too short', 400
        return 'OK', 200

    @staticmethod
    def check_login(login):  # check if login is unique and correct
        if login is None:
            return 'Login is empty', 400
        if len(login) > 30:
            return 'Login is too long', 400
        rows = User.query.filter_by(login=login).all()
        if len(rows) > 0:
            return 'Login already exists', 409
        else:
            return 'OK', 200

    @staticmethod
    def check_phone(phone, id=-1):  # check if phone is correct
        user = User.query.filter_by(phone=phone).first()
        if user is not None and user.id != id:
            return 'Phone already exists', 409

        pat = '^\+7\d{10}$'
        if re.match(pat, phone) is None:
            return 'Phone is incorrect', 400
        else:
            return 'OK', 200

    @staticmethod
    def check_is_public(isPublic):
        if isPublic not in [True, False]:
            return 'isPublic is incorrect', 400
        else:
            return 'OK', 200

    def is_my_friend(self, user_id):
        return user_id in [friend.id for friend in self.friend_of]

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    alpha2 = db.Column(db.String(2), nullable=False)
    public = db.Column(db.Boolean, nullable=False)
    phone = db.Column(db.String(15))
    image = db.Column(db.String(255))
    sessions = db.relationship('Session', backref='user', lazy=True)
    friends = db.relationship(
        "User",
        secondary="friendship",
        primaryjoin="User.id==Friendship.user_id",
        secondaryjoin="User.id==Friendship.friend_id",
        backref="friend_of"
    )


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    is_open = db.Column(db.Boolean, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id
        self.is_open = True
        self.deadline = datetime.datetime.now() + datetime.timedelta(days=1)

    def close(self):
        self.is_open = False
        (db.session.commit())


class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, user_id, friend_id):
        self.user_id = user_id
        self.friend_id = friend_id


