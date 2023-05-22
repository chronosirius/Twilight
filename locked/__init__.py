from flask import Blueprint, request, redirect, url_for, flash, g
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from os import environ as env
from main import security, users, servers

locked_bp = Blueprint('locked', __name__.split('.')[0], template_folder='templates/locked/')

@locked_bp.before_request
def check_authorization():
    t = request.cookies.get('authtoken', request.args.get('authtoken', request.form.get('authtoken', ''))).strip(' ') #type: ignore
    if t == '':
        flash('Please log in again.')
        return redirect(url_for('accounts.login'))
    try:
        try:
            data, timestamp = URLSafeTimedSerializer(env['SECRET_KEY'], salt=b'authtoken').loads(t, max_age=60*60*24*30, return_timestamp=True)
        except SignatureExpired:
            data, timestamp = URLSafeTimedSerializer(env['SECRET_KEY'], salt=b'authtoken').loads(t, return_timestamp=True)
            del security[data['email']]['auth_tokens'][data['token']]
            raise
        print(timestamp.timestamp())
        email = data['email']
        token = data['token']
        usertype = data['type']
        if usertype == 'bot':
            raise ValueError
    except (BadSignature, KeyError):
        flash('Invalid authtoken!')
        return redirect(url_for('accounts.login'))
    except ValueError:
        return {
            "success": False,
            "code": 418,
            "message": "This portion of the server cannot serve your request. Please use the API."
        }, 418
    if email not in security.keys():
        flash('That email is not registered!')
        return redirect(url_for('accounts.signup'))
    if token not in security[email]['auth_tokens'].keys(): #type: ignore
        flash('You have been logged out.')
        return redirect(url_for('accounts.login'))
    
    g.id = security[email]['id']
    g.user = users[security[email]['id']]
    #expires authtokens unused for 10 days (that isn't the currently being used one)
    for ttoken in security[email]['auth_tokens'].keys(): #type: ignore
        if ttoken != token and security[email]['auth_tokens'][ttoken]['last_used']['unix_ts'] + 10*24*60*60 <= type(timestamp).utcnow().timestamp(): #type: ignore
            del security[data['email']]['auth_tokens'][data['token']]
    security[email]['auth_tokens'][token]['last_used'] = {
        'unix_ts': round(type(timestamp).utcnow().timestamp()),
        "ip": g.remote_addr,
        "user_agent": request.user_agent.string
    }
    print(data)
    print(servers)

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
        servers=[servers[sid] for sid in [s['id'] for s in g.user['servers']]], #type: ignore
        get_user_details=get_user_details,
        get_server_details=get_server_details,
        check_in_server=check_in_server
    )

from .me import me_bp
from .server import servers_bp

locked_bp.register_blueprint(me_bp)
locked_bp.register_blueprint(servers_bp)