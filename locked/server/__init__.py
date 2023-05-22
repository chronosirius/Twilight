import os
from flask import Blueprint, request, redirect, url_for, abort, g, render_template as rt
from main import servers, users
from utils.func import crop_max_square, generate_token, get_timestamp 
from utils.permissions import ADMIN, BASIC, calculate_perms
from PIL import Image

servers_bp = Blueprint('servers', __name__.split('.')[0], url_prefix='/servers/', template_folder="../templates/locked/servers/")

@servers_bp.before_request
def check_servers():
    if request.path.split('/')[2] == 'create':
        return
    if request.path.split('/')[2] not in servers.keys():
        abort(404)
    if len(request.path.split('/')) == 3 or request.path.split('/')[3] == '':
        return redirect(url_for('locked.servers.server_home', sid=request.path.split('/')[2]))
    g.server = servers[request.path.split('/')[2]]

@servers_bp.context_processor
def ctx_processor():
    if g.get('server'):
        return dict(
            server=g.server
        )
    else:
        return dict()
    
@servers_bp.route('/create', methods=['POST'])
def server_create():
    if request.form.get('servername', '') != '':
        sid = generate_token()
        servers[sid] = {
            'members': {
                g.id: {
                    'roles': ['owner']
                }
            },
            'name': request.form['servername'],
            'id': sid,
            'link': f'/servers/{sid}/home',
            'channels': {
                (start_cid := generate_token()): {
                    'id': start_cid,
                    'name': 'start',
                    'flags': [],
                    'material_symbol': 'tag',
                    'history': [],
                    'category': 'ungrouped',
                    'overwrites': []
                }
            },
            'description': '',
            'welcome_message': 'Welcome to the server!',
            'roles': {
                'owner': {
                    'permissions': ADMIN,
                    'flags': ['BADGE', 'INVISIBLE'],
                    'badge': {
                        'text': 'Server Owner',
                        'img': '/cdn/default_badges/owner.svg'
                    },
                    'index': 'top'
                },
                "normal": {
                    'permissions': BASIC,
                    'flags': ['INVISIBLE'],
                    'index': 'bottom'
                }
            },
            "invites": []
        }
        if request.files['icon'].filename != '':
            im = crop_max_square(Image.open(request.files['icon'].stream)).convert('RGB')
            os.makedirs(f'storage/cdn/servers/{sid}/', exist_ok=True)
            im.save(f'storage/cdn/servers/{sid}/icon.webp', 'WEBP')
            servers[sid]['icon'] = f'/cdn/servers/{sid}/icon.webp'
        else:
            servers[sid]['icon'] = '/cdn/__default_server__.png'
        
        users[g.id]['servers'].append({ #type: ignore
            'id': sid,
            'me': {
                'nickname': users[g.id]['username'],
                'joined_at': get_timestamp(),
                'nickname_default': True
            }
        })
        return redirect(url_for('locked.servers.server_home', sid=sid))
    return {
        "message": 'Field "servername" is not filled.',
        'code': 400
    }, 400

@servers_bp.route('/<sid>/home')
def server_home(sid):
    totperms = calculate_perms(servers[sid], g.id)
    return rt('locked/servers/home.html',
        server=servers[sid],
        perms=totperms,
        servername=servers[sid]['name'],
        channels=servers[sid]['channels'],
        sid=sid,
        channel={
            'name': 'Home'
        })