
""" フォームから変数を受け取り、DBにCRUD操作をするコントローラ """

from flask import (
    Flask, render_template, request, redirect, url_for, flash, 
    session, 
)
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime

# postgresqlではデータ格納先のpath指定もmigrateも行わない
app = Flask(__name__)
from flaskr.models import db, User, UserConnect
from flaskr.forms import (
    LoginForm, RegisterForm, SettingForm, UserSearchForm, 
    ConnectForm, 
)

@app.route('/', methods=['GET'])
def home():
    connect_form = ConnectForm()
    friends = requested_friends = None
    if current_user.is_authenticated:
        friends = User.select_friends()
        requested_friends = User.select_requested_friends()
    return render_template('home.html', 
    friends=friends, requested_friends=requested_friends, connect_form=connect_form)


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


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """ 要はパスワードをアップグレードしたい """
    form = LoginForm(request.form)
    user = None
    if request.method == 'POST':
        email = form.email.data
        user = User.select_by_email(email)
        if form.password.data:
            with db.session.begin(subtransactions=True):
                user.reset_password(form.password.data)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('forgot_password.html', form=form, user=user)
    return render_template('forgot_password.html', form=form, user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    form = SettingForm(request.form)
    user_id = current_user.get_id()
    if request.method == 'POST':
        user = User.select_by_id(user_id)
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.email = form.email.data
            user.update_at = datetime.now()
            if form.comment.data:
                user.comment = form.comment.data
            # fileの中身を読込
            file = request.files[form.picture_path.name].read()
            if file:
                file_name = user_id + '_' + str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flaskr/static/user_images/' + file_name
                # picture_pathの箱にfileの中身を書き込む
                open(picture_path, 'wb').write(file)
                user.picture_path = 'user_images/' + file_name
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('setting.html', form=form)


@app.route('/user_search', methods=['GET', 'POST'])
@login_required
def user_search():
    form = UserSearchForm(request.form)
    connect_form = ConnectForm()
    # /user_connectに遷移するためのsessionを取得
    # session['url'] = 'user_search'
    users = None
    if request.method == 'POST' and form.validate():
        users = User.select_by_username(form.username.data)
        if users:
            return render_template('user_search.html', form=form, connect_form=connect_form, users=users)
        flash('ユーザが存在しません')
    return render_template('user_search.html', form=form, connect_form=connect_form, users=users)


@app.route('/user_connect', methods=['POST'])
@login_required
def user_connect():
    form = ConnectForm(request.form)
    if form.connect_status.data == 'apply':
        from_user_id = current_user.get_id()
        to_user_id = form.to_user_id.data
        connect = UserConnect(from_user_id, to_user_id, status=1)
        with db.session.begin(subtransactions=True):
            db.session.add(connect)
        db.session.commit()
    elif form.connect_status.data == 'approve':
        from_user_id = form.to_user_id.data
        to_user_id = current_user.get_id()
        connect = UserConnect.select_connect(from_user_id, to_user_id)
        with db.session.begin(subtransactions=True):
            connect.status = 2
        db.session.commit()
    # next_url = session.pop('url', 'home')
    return redirect(url_for('home'))


@app.route('/delete_connect', methods=['POST'])
@login_required
def delete_connect():
    id = request.form['id']
    connect = UserConnect.select_id(id, current_user.get_id())
    with db.session.begin(subtransactions=True):
        db.session.delete(connect)
    db.session.commit()
    return redirect(url_for('home'))



