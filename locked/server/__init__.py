import os
from flask import Blueprint, request, redirect, url_for, abort, g, render_template as rt
from main import servers, users
from utils.func import crop_max_square, generate_token, get_timestamp, list_to_dict, reorder_index
from utils.permissions import ADMIN, BASIC, calculate_perms
from PIL import Image

def resolve_members(srv):
    p = list()
    for id, member in srv['members'].items():
        member['id'] = id
        totperms = calculate_perms(srv, member['id'])
        n = {
            'id': member['id'],
            'vismember': list_to_dict(users[member['id']]['servers'])[srv['id']]['me'], #type: ignore
            'roles': [srv['roles'][role] for role in member['roles'] if 'INVISIBLE' not in srv['roles'][role]['flags']],
            'serverbadges': [srv['roles'][role]['badge'] for role in member['roles'] if 'BADGE' in srv['roles'][role]['flags']],
            'regbadges': [badge for badge in users[member['id']]['badges']],
            'joinedat': users[member['id']]['joined_at'],
            'permissions': totperms,
            'pfp_url': users[member['id']]['pfp_url']
        }
        try:
            n['top_role'] = reorder_index(n['roles'])[0]
        except:
            n['top_role'] = {
                'color': 'var(--text-color)'
            }
        p.append(n)
    return p


servers_bp = Blueprint('servers', __name__.split('.')[0], url_prefix='/servers/', template_folder="../templates/locked/servers/")

@servers_bp.before_request
def check_servers():
    if request.path.split('/')[2] == 'create':
        return #flask can't tell the difference between no return statement and a return (None) so I can do this
    if request.path.split('/')[2] not in servers.keys():
        abort(404)
    if len(request.path.split('/')) == 3 or request.path.split('/')[3] == '':
        return redirect(url_for('locked.servers.server_home', sid=request.path.split('/')[2]))
    g.server = servers[request.path.split('/')[2]]

@servers_bp.context_processor
def ctx_processor():
    if g.get('server'):
        return dict(
            server=g.server,
            perms=calculate_perms(g.server, g.id)
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
                'ungrouped': {
                    (start_cid := generate_token()): {
                        'id': start_cid,
                        'name': 'start',
                        'flags': [],
                        'material_symbol': 'tag',
                        'history': [],
                        'category': 'ungrouped',
                        'overwrites': []
                    }
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

@servers_bp.route('/<sid>/members')
def members(sid):
    return rt('locked/servers/members.html', members=resolve_members(g.server))

@servers_bp.route('/<sid>/channels/<cid>')
def channel(sid, cid):
    if cid not in servers[sid]['channels'].keys(): #type: ignore
        abort(404)
    return rt('locked/servers/channel.html', 

    )