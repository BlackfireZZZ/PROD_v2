from flask import request, jsonify
from flask_login import login_required, current_user

from . import app
from .models import User, Session


@app.route('/api/profiles/<login>', methods=['GET'])
@login_required
def get_profile_by_login(login):
    searched_user = User.query.filter_by(login=login).first()
    if searched_user is None:
        return jsonify({'reason': 'Incorrect login'}), 403
    if searched_user.public is True or searched_user.id == current_user.id:
        response = searched_user.get_info()
        return jsonify(response), 200
    else:
        return jsonify({'reason': 'You have no access to see profile'}), 403


@app.route('/api/ping', methods=['GET'])
def response_ping():
    return jsonify({"status": "ok"}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'reason': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'reason': 'Internal error'}), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'reason': 'Bad request'}), 400