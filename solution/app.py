from application import *
from application.handle_user.user_routes import user_blueprint
from application.handle_counrty.country_routes import country_blueprint
from application.handle_auth.auth_routes import auth_blueprint
from application.handle_friends.friends_routed import friends_blueprint

app.register_blueprint(user_blueprint, url_prefix='/api/me')
app.register_blueprint(country_blueprint, url_prefix='/api/countries')
app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
app.register_blueprint(friends_blueprint, url_prefix='/api/friends')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
