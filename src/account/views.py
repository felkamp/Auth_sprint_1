from flask import Blueprint
from flask_login import login_required

account = Blueprint('account', __name__)


@account.route('/login', methods=['GET', 'POST'])
def login():
    return 'user login'


@account.route('/register', methods=['GET', 'POST'])
def register():
    pass


@account.route('/logout')
@login_required
def logout():
    pass
