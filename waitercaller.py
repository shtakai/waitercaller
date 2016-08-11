from flask import Flask
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template

from flask.ext.login import LoginManager
from flask.ext.login import login_required
from flask.ext.login import login_user

from mockdbhelper import MockDBHelper as DBHelper
from user import User

from os.path import join, dirname
from dotenv import load_dotenv
import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
login_manager = LoginManager(app)
DB = DBHelper()

app.secret_key = os.environ['SECRET_KEY']


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user_password = DB.get_user(email)
    if user_password and user_password == password:
        user = User(email)
        login_user(user)
        return redirect(url_for('account'))
    return home()


@app.route('/account')
@login_required
def account():
    return "You are logged in"


@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
