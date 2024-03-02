from flask import Blueprint
from flask import request, jsonify
from flask_login import login_required, current_user
from application import app
from application import db
from application.models import User, Friendship
from application.db_countries import Countries


friends_blueprint = Blueprint('friends', __name__)


@friends_blueprint.route('/add', methods=['POST'])
@login_required
def add():
    data = request.json
    friend_login = data['login']
    friend = User.query.filter_by(login=friend_login).first()
    if friend is None:
        return jsonify({"reason": "User not found"}), 404
    if friend.id == current_user.id:
        return jsonify({"status": "ok"}), 200
    if not current_user.is_my_friend(friend.id) and friend.public is False:
        return jsonify({"reason": "Access denied"}), 401
    friendship = Friendship(current_user.id, friend.id)
    db.session.add(friendship)
    db.session.commit()
    return jsonify({"status": "ok"}), 200


@friends_blueprint.route('/remove', methods=['GET'])
@login_required
def remove():
    data = request.json
    friend_login = data['login']
    friend = User.query.filter_by(login=friend_login).first()
    if friend is None:
        return jsonify({"reason": "User not found"}), 404
    friendship = Friendship.query.filter_by(user_id=current_user.id, friend_id=friend.id).first()
    db.session.delete(friendship)
    db.session.commit()
    return jsonify({"status": "ok"}), 200


@friends_blueprint.route('/', methods=['GET'])
def get():
    data = request.json
    limit = data['limit']
    offset = data['offset']
    response = current_user.get_friends()
    response = response[offset:min(offset+limit, len(response))]
    return jsonify(response), 200