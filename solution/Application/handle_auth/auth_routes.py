from flask import Blueprint
from flask import request, jsonify
from application import app
from application import db
import os
from application.models import User, Session
from application.db_countries import Countries
import secrets

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/register', methods=['POST'])
def registration():  # register new user
    data = request.json
    login = data['login']
    check_log = User.check_login(login)
    if check_log[0] != 'OK':
        return jsonify({"reason": check_log[0]}), check_log[1]

    email = data['email']
    check_mail = User.check_email(email)
    if check_mail[0] != 'OK':
        return jsonify({"reason": check_mail[0]}), check_mail[1]

    password = data['password']
    check_pass = User.check_password(password)
    if check_pass[0] != 'OK':
        return jsonify({"reason": check_pass[0]}), check_pass[1]

    countryCode = data['countryCode']
    check_code = Countries.check_country_code(countryCode)
    if check_code[0] != 'OK':
        return jsonify({"reason": check_code[0]}), check_code[1]

    isPublic = data['isPublic']
    new_user = User(login, email, password, countryCode, isPublic)

    if 'phone' in data:
        new_user.phone = data['phone']
        check_ph = User.check_phone(new_user.phone)
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


@auth_blueprint.route('/sign-in', methods=['POST'])
def sign():
    data = request.json
    login = data['login']

    password = data['password']
    if None in [login, password]:
        return jsonify({'reason': 'Login or password is empty'}), 400

    user = User.query.filter_by(login=login).first()
    if user is None:
        return jsonify({'reason': 'Login or password is incorrect'}), 400
    if not user.match_passwords(password):
        return jsonify({"reason": "bad password"}), 400

    session = Session(secrets.token_hex(16),
                      user.id)
    db.session.commit()
    db.session.add(session)
    db.session.commit()
    return jsonify({"session": session.token}), 200