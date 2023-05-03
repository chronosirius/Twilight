from flask import Blueprint, render_template

account_bp_views = Blueprint('accounts', __name__.split('.')[0], url_prefix='/account')

@account_bp_views.route('/login')
def login():
    return render_template("accounts/login.html")

@account_bp_views.route('/signup')
def signup():
    return render_template('accounts/signup.html')