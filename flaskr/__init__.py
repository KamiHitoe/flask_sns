
from flaskr.views import app
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_message = 'ログインしてくださいね～'
app.config["SECRET_KEY"] = 'mysecret'

