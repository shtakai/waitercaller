from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.login import login_required

app = Flask(__name__)
login_manager = LoginManager(app)


@app.route('/')
def home():
    return "Under construction"


@app.route('/account')
@login_required
def account():
    return "You are logged in"


if __name__ == '__main__':
    app.run(port=5000, debug=True)
