from .models import User, Session
from Application import login_manager


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
    session_id = login.replace('Bearer ', '', 1)
    session = Session.query.filter_by(sessionid=session_id).first()
    if session is None:
        return None
    user = User.query.filter_by(login=session.user_login).first()
    return user

