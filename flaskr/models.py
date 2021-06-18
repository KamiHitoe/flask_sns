
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from flaskr.views import app
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://postgres:admin@localhost/flask_sns'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = 'mysecret'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_message = 'ログインしてくださいね～'


@login_manager.user_loader
def load_user(user_id):
    """ user_idに対して、Userインスタンスを返す """
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    """
    postgreでは__tablename__はいらない
    ログインセッションを管理するのでUserMixinを継承する必要がある
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    email = db.Column(db.String(32), index=True, unique=True)
    password = db.Column(db.Text)
    picture_path = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)  # login_managerで必要
    create_at = db.Column(db.DateTime, default=datetime.now)  # datetime.now()では変になる
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password).decode('utf8')

    def check_password(self, password):
        """ パスワードをチェックしてTrue/Falseを返す """
        return check_password_hash(self.password, password)

    @classmethod
    def select_by_email(cls, email):
        """ Userクラスからemailに合致したインスタンスを返す """
        return cls.query.filter_by(email=email).first()


