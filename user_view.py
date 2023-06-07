from flask import Blueprint, request, render_template, flash, redirect, url_for, g
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from os import environ as env
from main import users, security

userbp = Blueprint("user", __name__.split('.')[0])

@userbp.before_request
def check_authorization():
    t = request.cookies.get('authtoken', request.args.get('authtoken', request.form.get('authtoken', ''))).strip(' ') #type: ignore
    if t == '':
        g.user = 'anonymous'
        return
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
    except (BadSignature, KeyError, SignatureExpired):
        g.user = 'anonymous'
        return
    except ValueError:
        return {
            "success": False,
            "code": 418,
            "message": "This portion of the server cannot serve your request. Please use the API."
        }, 418
    if email not in security.keys():
        g.user = 'anonymous'
        return
    if token not in security[email]['auth_tokens'].keys(): #type: ignore
        g.user = 'anonymous'
        return
    
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

@userbp.route('/<uid>')
def user(uid):
    if uid in users.keys():
        if request.headers.get('X-TWILIGHT-Is-Iframe'):
            
            return render_template('iframe/user.html', user=users[uid])