from os import environ as env
from traceback import format_exc
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, send_from_directory, render_template, url_for, g
from werkzeug.exceptions import NotFound, HTTPException

from datetime import datetime as dt, timedelta as td

from utils.func import list_to_dict, generate_token
from utils.permissions import has_perm

from requests import get

from db import Database

servers = Database('storage/db/servers/')
users = Database('storage/db/users/')
security = Database('storage/db/security/')
dms = Database('storage/db/directmessages/')
security = Database('storage/db/security/')
invites = Database('storage/db/invites/')

consolecode = generate_token()[0:15]

app = Flask(__name__)

app.config['SECRET_KEY'] = env['SECRET_KEY']
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'storage/sessions/'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = td(days=30)

@app.before_request
def before():
    r = str(request.headers.get('X-Forwarded-For', ''))
    g.remote_addr = r or request.remote_addr
    if r != '':
        request.remote_addr = r

@app.route('/')
def index():
    return render_template('index.html'), 200

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico')

@app.errorhandler(404)
def not_found(err: NotFound):
    return render_template('err/404.html', error_path=request.path), 404

@app.route('/static/push_mention.js')
def sw_push():
    r = send_from_directory('static', 'push_mention.js')
    r.headers.add_header('Service-Worker-Allowed', "/")
    return r
    
@app.route('/static/cache.js')
def sw_cache():
    r = send_from_directory('static', 'cache.js')
    r.headers.add_header('Service-Worker-Allowed', "/")
    return r

@app.route('/firebug-lite-debug.js')
def firebug():
    rj = get('https://luphoria.com/fbl/fbl/firebug-lite-debug.js')
    rq = send_from_directory('static', 'firebug-lite-debug.js')
    return rq

@app.route('/firebug/<path:path>')
def firebug2(path):
    return send_from_directory('firebug-lite-master', path)

@app.errorhandler(Exception)
def internal_error(err):
    if not isinstance(err, HTTPException):
        erre = format_exc()
        ee = erre.replace('\n', '<br>\n')
        with open('log.txt', 'a') as log:
                logstr = \
    f"""
    <code>
        Exception occured at <i>{dt.utcnow().strftime('%m/%d/%y %H:%M:%S')}</i>:<br>
        {type(err).__name__}: {err}<br><br>
        {ee.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('&lt;br&gt;', '<br>')}
        </span>
    </code>
    <br>
    <br>
    <br>
    """
                log.write(logstr)
        if app.debug:
            raise err
        return render_template('err/500.html', err=err), 500
    return err

@app.context_processor
def base_template_ctx():
    return dict(
        host=url_for('index', _external=True).rstrip('/'),
        version='W3-A-0.0.0',
        ltd=list_to_dict,
        has_perm=has_perm,
        appname='Twilight'
    )

def load():
    from account import account_bp_views
    from userauth import userauth_bp_proc
    from locked import locked_bp
    from cdn import cdn

    app.register_blueprint(account_bp_views)
    app.register_blueprint(userauth_bp_proc)
    app.register_blueprint(locked_bp)
    app.register_blueprint(cdn)

from websocket import wss
def run():
    load()
    wss.init_app(app)
    wss.run(app, '0.0.0.0', port=int(env['PORT']), debug=True)

if __name__ == "__main__":
    run()