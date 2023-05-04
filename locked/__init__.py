from flask import Blueprint, request, redirect, url_for, flash, g
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from os import environ as env
from main import security, users, servers

locked_bp = Blueprint('locked', __name__.split('.')[0], template_folder='templates/locked/')

@locked_bp.before_request
def check_authorization():
    t = request.cookies.get('authtoken', request.args.get('authtoken', request.form.get('authtoken', ''))).strip(' ') #type: ignore
    if t == '':
        flash('Invalid authtoken!')
        return redirect(url_for('accounts.login'))
    try:
        data, timestamp = URLSafeTimedSerializer(env['SECRET_KEY'], salt=b'authtoken').loads(t, max_age=60*60*24*30, return_timestamp=True)
        print(timestamp.timestamp())
        email = data['email']
        token = data['token']
        usertype = data['type']
        if usertype == 'bot':
            raise ValueError
    except (BadSignature, SignatureExpired, KeyError):
        flash('Invalid authtoken!')
        return redirect(url_for('accounts.login'))
    except ValueError:
        return {
            "code": 418,
            "message": "This portion of the server cannot serve your request. Please use the API."
        }, 418
    if email not in security.keys():
        flash('That email is not registered!')
        return redirect(url_for('accounts.signup'))
    if token not in security[email]['auth_tokens']:
        flash('You have been logged out.')
        return redirect(url_for('accounts.login'))
    
    g.id = security[email]['id']
    g.user = users[security[email]['id']]
    print(data)

@locked_bp.context_processor
def jinja_context_locked():
    def get_user_details(id):
        if id in users.keys():
            return users['id']
        else:
            return {
                'name': 'Deleted User',
                'pfp_url': '/cdn/__default_user__.webp'
            }
    def get_server_details(id):
        if id in servers.keys():
            return servers[id]
        
    def check_in_server(id):
        if id in servers.keys():
            return (g.id in servers[id]['members'].keys()) #type: ignore
    return dict(
        user=g.user,
        servers=[servers[sid] for sid in [s['id'] for s in g.user['servers']]],
        get_user_details=get_user_details,
        get_server_details=get_server_details,
        check_in_server=check_in_server
    )

from .me import me_bp

locked_bp.register_blueprint(me_bp)