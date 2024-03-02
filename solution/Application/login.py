from flask import jsonify
from .models import User, Session
from application import login_manager
import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.request_loader
def request_loader(request):
    login = request.headers.get('Authorization')
    if login is None:
        return None
    if not login.startswith('Bearer '):
        return None
    token = login.replace('Bearer ', '', 1)
    session = Session.query.filter_by(token=token).first()
    if session is None:
        return None
    if session.is_open is False:
        return None
    if session.deadline < datetime.datetime.now():
        session.close()
        return None
    user = User.query.filter_by(id=session.user_id).first()
    return user


@login_manager.unauthorized_handler
def handle_unauthorized():
    return jsonify({"reason": "unauthorized"}), 401

