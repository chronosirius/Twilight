from re import match
from flask import Blueprint, flash, g, request, render_template as rt, redirect, session, url_for
from main import security, users
from itsdangerous import BadSignature, URLSafeSerializer, URLSafeTimedSerializer
from os import environ as env
from utils.func import generate_token, quickhash
from utils.constants import blocked_symbols
from mail import send
from datetime import datetime as dt

BLOCKLIST=['ab7400@pleasantonusd.net', 'arnanbajaj@gmail.com']

def generate_discriminator(username):
    retries = 0
    nds = [user['username']+'/'+user['discriminator'] for user in users.values()] #type: ignore
    while retries <= 20:
        disc = str(int(generate_token(), 16))[0:6]
        if username+'/'+disc not in nds:
            return disc
        retries += 1
    raise TimeoutError('Too many users have this username...')
        
userauth_bp_proc = Blueprint('userauth', __name__.split('.')[0], url_prefix='/auth')
s = URLSafeSerializer(env['SECRET_KEY'], salt=b'_email_verify')
st = URLSafeTimedSerializer(env['SECRET_KEY'], salt=b'authtoken')

@userauth_bp_proc.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('username', '').strip(' ') #type: ignore
    password = request.form.get('password', '').strip(' ') #type: ignore
    if (email != '') and match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email) and (email not in BLOCKLIST) and \
    (password != ''): #type: ignore
        print(email, password)
        if email not in security.keys():
            tk = s.dumps({'email': email, 'password': quickhash(password), 'prefilled': request.form.get('display_username', '')})
            send(email, 'Wecome to Twilight!', rt('email/intro.jineml', token=tk), 'Twilight Mailer')
            flash('Go check your email. It may take a minute or so.')
            session['pending'] = True
            return redirect(url_for('accounts.signup'))
        else:
            flash('That email is taken!')
            return redirect(url_for('accounts.signup'))
    else:
        flash('Please fill all fields!')
        return redirect(url_for('accounts.signup'))

@userauth_bp_proc.route('/signup/finish', methods=['GET', 'POST'])
def signup_finish():
    if request.method == 'POST':
        if (request.form.get('token', '').strip(' ') != '') and (request.form.get('password', '').strip(' ') != '') and (request.form.get('username', '').strip(' ') != ''): #type: ignore
            try:
                a = s.loads(request.form.get('token', '').strip(' ')) #type: ignore
            except BadSignature:
                flash('Invalid verification URL! To resend, please re-enter your info.')
                return redirect(url_for('accounts.signup'))
            if a['email'] in security.keys():
                flash('The signup for that email is done already!')
                return redirect(url_for('accounts.signup'))
            if a['password'] == quickhash(request.form['password']):
                uid = generate_token()
                security[a['email']] = {
                    'password': a['password'],
                    'id': uid,
                    'auth_tokens': {}
                }
                username = request.form['username']
                for sym in blocked_symbols:
                    username = username.replace(sym, '')
                username = username.replace('-', '_')
                username.strip(' ')
                try:
                    disc = generate_discriminator(username)
                except TimeoutError:
                    flash('Too many users have that username!')
                    return redirect(url_for('userauth.signup_finish', token=request.form.get('token', '')))
                users[uid] = {
                    'username': username,
                    'discriminator': disc,
                    'servers': [],
                    'friends': [],
                    'friend_requests': {
                        'outgoing': [],
                        'incoming': []
                    },
                    'emails': [a['email']],
                    'pfp_url': '/cdn/__default_user__.webp',
                    'status': 'online',
                    'id': uid,
                    'blocked': [],
                    'joined_at': round(dt.utcnow().timestamp()),
                    'badges': [],
                    'notify': [],
                    'privacy': 1 #0 - friends & server members only, 1 - users only, 2 - anyone
                }
                #session.clear()
                session['uid'] = uid
                authtoken_premature = generate_token()[0:15]
                authtoken = str(st.dumps({
                    'email': a['email'],
                    'token': authtoken_premature,
                    'type': 'user'
                }))
                security[a['email']]['auth_tokens'][authtoken_premature] = {
                    "created":{
                        'unix_ts': round(dt.utcnow().timestamp()),
                        "ip": g.remote_addr,
                        "user_agent": request.user_agent.string
                    },
                    "token": authtoken_premature,
                    "last_used":{
                        'unix_ts': round(dt.utcnow().timestamp()),
                        "ip": g.remote_addr,
                        "user_agent": request.user_agent.string
                    },
                }
                r = redirect(url_for('locked.me.me_main'))
                r.set_cookie('authtoken', authtoken)
                return r
            else:
                flash('Incorrect password!')
                return redirect(url_for('userauth.signup_finish', token=request.form['token']))
        else:
            flash('Please fill all fields.')
            return redirect(url_for('userauth.signup_finish', token=request.form.get('token')))
    # GET
    tk = request.args.get('token', '').strip(' ') #type: ignore
    if tk != '':
        try:
            a = s.loads(tk)
            if a['email'] in security.keys():
                flash('The signup for that email is done already!')
                return redirect(url_for('accounts.signup'))
        except BadSignature:
            flash('Invalid verification URL! To resend, please re-enter your info.')
            return redirect(url_for('accounts.signup'))
        else:
            return rt('accounts/signup_finish.html', token=tk, prefilled_name=a['prefilled'])
    else:
        flash('You didn\'t provide a verification token!')
        return redirect(url_for('accounts.signup'))

@userauth_bp_proc.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip(' ') #type: ignore
    if (email != '' and match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email)) and \
        (request.form.get('password', '').strip(' ') != ''): #type: ignore
        if request.form['email'] in security.keys():
            if quickhash(request.form['password']) == security[request.form['email']]['password']:
                session['uid'] = security[request.form['email']]['id']
                r = redirect(url_for('locked.me.me_main'))
                token_premature = generate_token()[0:15]
                security[request.form['email']]['auth_tokens'][token_premature] = {
                    "created":{
                        'unix_ts': round(dt.utcnow().timestamp()),
                        "ip": g.remote_addr,
                        "user_agent": request.user_agent.string
                    },
                    "token": token_premature,
                    "last_used":{
                        'unix_ts': round(dt.utcnow().timestamp()),
                        "ip": g.remote_addr,
                        "user_agent": request.user_agent.string
                    }
                }
                token = str(st.dumps({
                    'email': request.form['email'],
                    'token': token_premature,
                    'type': 'user'
                }))
                r.set_cookie('authtoken', token, path="/")
                return r
            else:
                flash('Incorrect password!')
                return redirect(url_for('accounts.login'))
        else:
            flash('That email is not registered!')
            return redirect(url_for('accounts.signup'))
    else:
        flash('Please fill all fields.')
        return redirect(url_for('accounts.login'))