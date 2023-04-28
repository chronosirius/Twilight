from json import JSONDecodeError
from os import environ as env
from traceback import format_exc
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, Blueprint, redirect, request, send_from_directory, render_template, url_for
from werkzeug.exceptions import NotFound, HTTPException

from datetime import datetime as dt, timedelta as td

from utils.func import list_to_dict, generate_token
from utils.permissions import has_perm

from db import Database

servers = Database('storage/db/servers/')
users = Database('storage/db/users/')
security = Database('storage/db/security/')
dms = Database('storage/db/directmessages/')

consolecode = generate_token()[0:15]

app = Flask(__name__)

app.config['SECRET_KEY'] = env['SECRET_KEY']
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'storage/sessions/'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = td(days=30)

from account import account_bp_views

app.register_blueprint(account_bp_views)

@app.route('/')
def index():
    return render_template('index.html'), 200

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico')

@app.errorhandler(404)
def not_found(err: NotFound):
    return render_template('err/404.html', error_path=request.path), 404

@app.errorhandler(Exception)
def internal_error(err):
    if not isinstance(err, JSONDecodeError):
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
            if __name__ == '__main__':
                raise err
        return render_template('err/500.html', err=err), 500
    return redirect(request.full_path.rstrip('?'))

@app.context_processor
def base_template_ctx():
    return dict(
        host=url_for('index', _external=True).rstrip('/'),
        version='W3-A-0.0.0',
        ltd=list_to_dict,
        has_perm=has_perm,
        appname='Twilight'
    )

from websocket import wss
def run():
    wss.init_app(app)
    wss.run(app, '0.0.0.0', port=int(env['PORT']), debug=True)

if __name__ == "__main__":
    run()