
from flask import (
    Flask, render_template, request
)
from flask_login import login_required

# postgresqlではデータ格納先のpath指定もmigrateも行わない
app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/login')
def login():
    return render_template('login.html')


