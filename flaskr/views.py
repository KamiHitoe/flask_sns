

from flask import (
    Flask, render_template, request, redirect, url_for, flash, 

)
from flask_login import login_required, login_user, logout_user, current_user

# postgresqlではデータ格納先のpath指定もmigrateも行わない
app = Flask(__name__)
from flaskr.models import db, User
from flaskr.forms import LoginForm, RegisterForm


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        user = User.select_by_email(email)
        if user and user.check_password(password):
            """ ユーザに対してログイン処理を施す """
            login_user(user)
            return redirect(url_for('home'))
        elif user:
            flash('パスワードが間違っています')
        else:
            flash('存在しないユーザです')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        user = User(username, email, password)
        with db.session.begin(subtransactions=True):
            db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user')
@login_required
def user():
    return 'login success'


