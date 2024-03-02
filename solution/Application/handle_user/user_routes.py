from flask import Blueprint
from flask import request, jsonify
from flask_login import login_required, current_user
from application import db
from application.models import User
from application.db_countries import Countries

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/profile', methods=['GET'])
@login_required
def get_profile():
    response = current_user.get_info()
    return jsonify(response), 200


@user_blueprint.route('/profile', methods=['PATCH'])
@login_required
def update_profile():
    data = request.json
    if 'countryCode' in data:
        new_alpha2 = data['countryCode']
        if not Countries.check_country_code(new_alpha2)[0] == 'OK':
            return jsonify({'reason': Countries.check_country_code(current_user.alpha2)[0]}), 401
        current_user.alpha2 = new_alpha2
    if 'isPublic' in data:
        new_isPublic = data['isPublic']
        if not User.check_is_public(new_isPublic)[0] == 'OK':
            return jsonify({'reason': User.check_is_public(current_user.public)[0]}), 401
        current_user.public = new_isPublic
    if 'phone' in data:
        new_phone = data['phone']
        if not User.check_phone(new_phone)[0] == 'OK':
            return jsonify({'reason': User.check_phone(current_user.phone, current_user.id)[0]}), 401
        current_user.phone = new_phone
    if 'image' in data:
        current_user.image = data['image']
    response = current_user.get_info()
    db.session.commit()
    return jsonify(response), 200


@user_blueprint.route('/updatePassword', methods=['POST'])
@login_required
def update_password():
    data = request.json
    old_password = data['oldPassword']
    new_password = data['newPassword']
    if current_user.match_passwords(old_password):
        if not User.check_password(new_password)[0] == 'OK':
            return jsonify({'reason': User.check_password(new_password)[0]}), 401
        current_user.update_password(new_password)
        for session in current_user.sessions:
            session.close()
        return jsonify({'status': 'ok'}), 200
    else:
        return jsonify({'reason': 'Incorrect password'}), 400
