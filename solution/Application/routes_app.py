from flask import Flask, request, jsonify
from . import app
from . import db
import os
from .models import User, Session
from .db_countries import Countries
from flask_login import LoginManager, login_user, login_required, current_user
import psycopg2
import re
import secrets


@app.route('/api/ping', methods=['GET'])
def send():
    return jsonify({"status": "ok"}), 200


def get_db_params():
    DB_username = os.environ.get('POSTGRES_USERNAME')
    DB_password = os.environ.get('POSTGRES_PASSWORD')
    DB_host = os.environ.get('POSTGRES_HOST')
    DB_port = os.environ.get('POSTGRES_PORT')
    DB_name = os.environ.get('POSTGRES_DATABASE')
    return DB_username, DB_password, DB_host, DB_port, DB_name


def check_login(login):   # check if login is unique and correct
    if login is None:
        return 'Login is empty', 400
    if len(login) > 30:
        return 'Login is too long', 400
    rows = User.query.filter_by(login=login).all()
    if len(rows) > 0:
        return 'Login already exists', 409
    else:
        return 'OK', 200


def check_email(email):     # check if email is unique and correct
    if email is None:
        return 'Email is empty', 400
    if len(email) > 50:
        return 'Email is too long', 400
    rows = User.query.filter_by(email=email).all()
    if len(rows) > 0:
        return 'Email already exists', 409
    else:
        return 'OK', 200


def check_password(password):     # check if password is correct
    if password is None:
        return 'Password is empty', 400
    if len(password) > 100:
        return 'Password is too long', 400
    if len(password) < 6:
        return 'Password is too short', 400
    return 'OK', 200


def check_country_code(countryCode):     # check if country code is correct
    print(countryCode)
    DB_username, DB_password, DB_host, DB_port, DB_name = get_db_params()
    conn = psycopg2.connect(dbname=DB_name, user=DB_username, password=DB_password, host=DB_host)
    cursor = conn.cursor()
    if countryCode is None:
        return 'Country code is empty', 400
    if len(countryCode) > 2:
        return 'Country code is too long', 400
    if len(countryCode) < 2:
        return 'Country code is too short', 400
    cursor.execute('SELECT * FROM countries WHERE %s = alpha2', (countryCode,))
    rows = cursor.fetchone()
    if rows is None:
        return 'Country code is incorrect', 400
    else:
        return 'OK', 200
    cursor.close()
    conn.close()


def check_phone(phone):     # check if phone is correct
    pat = '^\+7\d{10}$'
    rows = User.query.filter_by(phone=phone).all()
    if rows is not None:
        return 'Phone already exists', 409
    if re.match(pat, phone) == None:
        return 'Phone is incorrect', 400
    else:
        return 'OK', 200


@app.route('/api/auth/register', methods=['POST'])
def registration():     # register new user
    data = request.json
    login = data['login']
    check_log = check_login(login)
    if check_log[0] != 'OK':
        return jsonify({"reason": check_log[0]}), check_log[1]
    email = data['email']
    check_mail = check_email(email)
    if check_mail[0] != 'OK':
        return jsonify({"reason": check_mail[0]}), check_mail[1]
    password = data['password']
    check_pass = check_password(password)
    if check_pass[0] != 'OK':
        return jsonify({"reason": check_pass[0]}), check_pass[1]
    countryCode = data['countryCode']
    check_code = check_country_code(countryCode)
    if check_code[0] != 'OK':
        return jsonify({"reason": check_code[0]}), check_code[1]
    isPublic = data['isPublic']
    new_user = User(login, email, password, countryCode, isPublic)
    if 'phone' in data:
        new_user.phone = data['phone']
        check_ph = check_phone(new_user.phone)
        if check_ph[0] != 'OK':
            return jsonify({"reason": check_ph[0]}), check_ph[1]
    if 'image' in data:
        new_user.image = data['image']
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"profile": {"login": login,
                    "email": email,
                    "countryCode": countryCode,
                    "isPublic": isPublic,
                    "phone": new_user.phone,
                    "image": new_user.image}
                    }), 200


@app.route('/api/auth/sign-in', methods=['POST'])
def sign():
    data = request.json
    login = data['login']
    password = data['password']
    if None in [login, password]:
        return jsonify({'reason': 'Login or password is empty'}), 400
    user = User.query.filter_by(login=login).first()
    if user is None:
        return jsonify({'reason': 'Login or password is incorrect'}), 400
    if not user.check_password_hash(password):
        return jsonify({"reason": "bad password"}), 400
    session = Session.query.filter_by(token=secrets.token_hex(16), user_id=user.id).first()
    db.session.add(session)
    db.session.commit()
    login_user(user)
    return jsonify({"session": session.token}), 200


@app.route('/api/me/profile', methods=['GET'])
@login_required
def get_profile():
    profile = {"login": current_user.login,
                "email": current_user.email,
                "countryCode": current_user.countryCode,
                "isPublic": current_user.isPublic
               }
    if current_user.phone is not None:
        profile['phone'] = current_user.phone
    if current_user.image is not None:
        profile['image'] = current_user.image
    return jsonify(profile), 400


@app.route('/api/countries', methods=['GET'])
def get_countries():
    DB_username, DB_password, DB_host, DB_port, DB_name = get_db_params()
    try:
        conn = psycopg2.connect(dbname=DB_name, user=DB_username, password=DB_password, host=DB_host)

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM countries")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    except:
        return jsonify({"status": "Cannot connect to database"}), 500


@app.route('/api/countries/{alpha2_code:string}', methods=['GET'])
def get_country(alpha2_code):
    DB_username, DB_password, DB_host, DB_port, DB_name = get_db_params()
    try:
        conn = psycopg2.connect(dbname=DB_name, user=DB_username, password=DB_password, host=DB_host)

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM countries WHERE %s = alpha2', (alpha2_code,))
        row = cursor.fetchone()
        if row is None:
            return jsonify({'reason': 'Country not found'}), 404
        cursor.close()
        conn.close()
        return jsonify(row), 200
    except:
        return jsonify({"status": "Cannot connect to database"}), 500