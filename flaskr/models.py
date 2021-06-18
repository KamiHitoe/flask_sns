
from flask_sqlalchemy import SQLAlchemy
from flaskr.views import app
from flaskr import login_manager

app.config['SECRET_KEY'] = 'hogehoge'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://postgres:admin@localhost/flask_sns'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    """ user_idに対して、Userインスタンスを返す """
    return User.query.get(user_id)


class User(db.Model):
    """ postgreでは__tablename__はいらない """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)

    def __init__(self, username):
        self.username = username
