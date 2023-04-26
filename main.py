from os import environ as env
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory, render_template, url_for

from datetime import datetime as dt, timedelta as td

from utils.func import list_to_dict
from utils.permissions import has_perm

app = Flask(__name__)

app.config['SECRET_KEY'] = env['SECRET_KEY']
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'storage/sessions/'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = td(days=30)

m = __import__('blueprints')

for bp in m.__dict__.values():
    app.register_blueprint(bp)

@app.route('/')
def index():
    return render_template('index.html'), 200

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico')

@app.context_processor
def base_template_ctx():
    return dict(
        host=url_for('index', _external=True).rstrip('/'),
        version='W3-A-0.0.0',
        ltd=list_to_dict,
        has_perm=has_perm,
        appname='Twilight'
    )

def run():
    app.run('0.0.0.0', port=int(env['PORT']))

if __name__ == "__main__":
    run()