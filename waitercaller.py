from flask import Flask
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template

from flask.ext.login import LoginManager
from flask.ext.login import login_required
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import current_user
import config

from forms import RegistrationForm
from forms import LoginForm
from forms import CreateTableForm

from mockdbhelper import MockDBHelper as DBHelper
from user import User
from passwordhelper import PasswordHelper
from bitlyhelper import BitlyHelper

from os.path import join, dirname
from dotenv import load_dotenv
import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
login_manager = LoginManager(app)
DB = DBHelper()
PH = PasswordHelper()
BH = BitlyHelper()

app.secret_key = os.environ['SECRET_KEY']


@app.route('/')
def home():
    return render_template("home.html", loginform=LoginForm(), registrationform=RegistrationForm())


@app.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        stored_user = DB.get_user(form.loginemail.data)
        if stored_user and PH.validate_password(form.loginpassword.data, stored_user['salt'], stored_user['hashed']):
            user = User(form.loginemail.data)
            login_user(user, remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append("Email or password invalid")
    return render_template("home.html", loginform=form, registrationform=RegistrationForm())


@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append("Email address already registered")
            return render_template("home.html", loginform=LoginForm(), registrationform=form)
        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data, salt, hashed)
        return render_template("home.html", loginform=LoginForm(), registrationform=form, onloadmessage="Registration successful. Please log in.")
    return render_template("home.html", loginform=LoginForm(), registrationform=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/account')
@login_required
def account():
    tables = DB.get_tables(current_user.get_id())
    return render_template("account.html", createtableform=CreateTableForm(), tables=tables)


@app.route('/account/createtable', methods=['POST'])
@login_required
def account_createtable():
    tablename = request.form.get('tablenumber')
    tableid = DB.add_table(tablename, current_user.get_id())
    new_url = BH.shorten_url(config.base_url + "newrequest/" + tableid)
    DB.update_table(tableid, new_url)
    return redirect(url_for('account'))


@app.route('/account/deletetable')
@login_required
def account_deletetable():
    tableid = request.args.get('tableid')
    DB.delete_table(tableid)
    return redirect(url_for('account'))


@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
