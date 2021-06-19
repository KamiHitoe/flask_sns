
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from flaskr.views import app
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
from flask import url_for
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import aliased


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
    """ ログインセッションを管理するUserテーブル """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    email = db.Column(db.String(32), index=True, unique=True)
    password = db.Column(db.Text)
    comment = db.Column(db.Text, default='')
    picture_path = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)  # login_managerで必要
    create_at = db.Column(db.DateTime, default=datetime.now)  # datetime.now()では変になる
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """ パスワードをチェックしてTrue/Falseを返す """
        return check_password_hash(self.password, password)

    def reset_password(self, password):
        self.password = generate_password_hash(password).decode('utf-8')

    @classmethod
    def search_by_email(cls, email):
        """ Userクラスからemailに合致したインスタンスを返す """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def search_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def search_by_username(cls, username):
        """ UserConnectと外部結合させた上でusernameでUserを検索 """
        user_connect1 = aliased(UserConnect)  # UserConnectと紐づけられたクエリ
        user_connect2 = aliased(UserConnect)
        return cls.query.filter(
            cls.username.like(f'%{username}%'),  # 両方向部分一致検索
            cls.id != int(current_user.get_id()),
        ).outerjoin(  # UserConnectと外部結合
            user_connect1,
            and_(  # fromが自分
                user_connect1.from_user_id == current_user.get_id(),
                user_connect1.to_user_id == cls.id,
            )
        ).outerjoin(
            user_connect2,
            and_(  # fromが相手
                user_connect2.from_user_id == cls.id,
                user_connect2.to_user_id == current_user.get_id(),
            )
        ).with_entities(
            cls.id, cls.username, cls.picture_path, cls.comment,
            user_connect1.status.label('joined_status_from_currentuser'),
            user_connect2.status.label('joined_status_from_user'),
        ).all()


    @classmethod
    def search_friends(cls):
        """ UserConnectを紐づけて、Userインスタンスを返す """
        return cls.query.join(
            UserConnect,
            or_(
                and_(
                    UserConnect.from_user_id == current_user.get_id(),
                    UserConnect.to_user_id == cls.id,  # 返す予定のユーザid
                    UserConnect.status == 2,
                ),
                and_(
                    UserConnect.from_user_id == cls.id,
                    UserConnect.to_user_id == current_user.get_id(),  # 返す予定のユーザid
                    UserConnect.status == 2,
                ),
            ),
        ).all()

    @classmethod
    def search_requested_friends(cls):
        return cls.query.join(
            UserConnect,
            and_(
                UserConnect.from_user_id == cls.id,
                UserConnect.to_user_id == current_user.get_id(),
                UserConnect.status == 1,
            ),
        ).all()


class UserConnect(db.Model):
    """ Userの友達状態を記録する、Userと外部結合させる """
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=0)
    create_at = db.Column(db.DateTime, default=datetime.now)  # datetime.now()では変になる
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, from_user_id, to_user_id, status=0):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.status = status

    @classmethod
    def search_connect(cls, from_user_id, to_user_id):
        return cls.query.filter_by(
            from_user_id = from_user_id,
            to_user_id = to_user_id
            ).first()

    @classmethod
    def search_id(cls, id1, id2):
        """ fromとtoの対応をするユーザのconnectを返す """
        return cls.query.filter(
            or_(
                and_(
                    UserConnect.from_user_id == id1,  # Class.が必要
                    UserConnect.to_user_id == id2,  # filter_byと違って== になる
                ),
                and_(
                    UserConnect.from_user_id == id2,
                    UserConnect.to_user_id == id1,
                ),
            ),
        ).first()


