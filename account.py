from flask import Blueprint

account_bp_views = Blueprint('accounts', __name__.split('.')[0], url_prefix='/account')

@account_bp_views.route('/login')
def login() -> str:
    return ""