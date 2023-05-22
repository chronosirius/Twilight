from flask import Blueprint, abort, g, redirect, render_template as rt, request, url_for
from jinja2 import TemplateNotFound
from main import users, dms
from utils.func import expose, generate_token

me_bp = Blueprint('me', __name__.split('.')[0], url_prefix='/me/', template_folder="../templates/locked/me/")

@me_bp.route('/')
def me_main():
    return rt('me.html')

@me_bp.route('/update_status', methods=['POST'])
def update_status():
    if request.form.get('status', '') != '':
        g.user['status'] = request.form['status']
        return {
            'code': 200,
            'message': f'Updated status to "{request.form["status"]}"',
            'success': True
        }, 200
    else:
        return {
            'code': 400,
            'message': 'A field value was missing. ("status")',
            'success': False
        }, 400

@me_bp.route('/friends/new')
def friend_new():
    return rt('friends/new.html')

@me_bp.route('/friends/pending')
def friends_pending():
    return rt('friends/pending.html', incoming=[users[uid] for uid in g.user['friend_requests']['incoming']], outgoing=[users[uid] for uid in g.user['friend_requests']['outgoing']])

@me_bp.route('/json')
def json():
    friendlist = [users[friend['id']] for friend in g.user['friends']]
    frienddict = dict()
    for f in friendlist:
        frienddict[f['id']] = expose(f, ['username', 'discriminator', 'pfp_url', 'status']) #type: ignore

    friend_requests_incoming = [users[incoming] for incoming in g.user['friend_requests']['incoming']]
    incoming_requests = dict()
    for f in friend_requests_incoming:
        incoming_requests[f['id']] = expose(f, ['username', 'discriminator', 'pfp_url', 'status']) #type: ignore

    friend_requests_outgoing = [users[outgoing] for outgoing in g.user['friend_requests']['outgoing']]
    outgoing_requests = dict()
    for f in friend_requests_outgoing:
        outgoing_requests[f['id']] = expose(f, ['username', 'discriminator', 'pfp_url', 'status']) #type: ignore

    return {
        'friends': frienddict,
        'friend_requests': {
            'outgoing': outgoing_requests,
            'incoming': incoming_requests
        }
    }

@me_bp.route('/settings/<page>')
def settings(page):
    try:
        if page == 'base':
            raise TemplateNotFound('base')
        response = rt(f'settings/{page}.html', user=g.user)
        return response
    except TemplateNotFound:
        abort(404)

@me_bp.route('/settings/')
@me_bp.route('/settings')
def settings_fallback():
    return redirect(url_for('locked.me.settings', page='overview'))

@me_bp.route('/fr/send', methods=['POST'])
def sendfr():
    if request.form.get('username', '') != '' and request.form.get('discriminator', '') != '':
        unique = request.form['username'] + "/" + request.form['discriminator']
        if unique != g.user['username']+"/"+g.user['discriminator']:
            for un, uid in [(user['username']+'/'+user['discriminator'], user['id']) for user in users.values()]: #type: ignore
                if unique == un:
                    if uid not in g.user['friend_requests']['outgoing'] and uid not in g.user['friends'] and uid not in g.user['friend_requests']['incoming']:
                        users[uid]['friend_requests']['incoming'].append(g.user['id']) #type: ignore
                        g.user['friend_requests']['outgoing'].append(uid)
                        return {
                            'success': True,
                            'message': 'Sent the friend request successfully!',
                            'code': 201
                        }, 201
                    else:
                        return {
                            'success': False,
                            'code': 409,
                            'message': 'We know you want to friend them. Perhaps try friending someone else?'
                        }, 409
                else:
                    continue
            return {
                'message': 'You\'re trying to send a friend request to a nonexistent person. Even trying to friend yourself would be better! (Call 988 - it\'s advisable.)',
                'code': 404,
                'success': False
            }, 404
        else:
            return {
                'success': False,
                'message': 'We know that your only friend is you, but you don\'t need to show that online, too.',
                'code': 400
            }, 400
    else:
        return {
            'message': 'A field value was missing. ANY_OR_ALL("username", "discriminator")',
            'code': 400,
            'success': False
        }, 400

@me_bp.route('/fr/accept', methods=['POST'])
def acceptfr():
    if request.form.get('acception', '') != '':
        acception = request.form['acception']
        if acception in g.user['friend_requests']['incoming'] and acception not in g.user['friends'] and acception in users.keys():
            g.user['friend_requests']['incoming'].remove(acception)
            users[acception]['friend_requests']['outgoing'].remove(g.id) #type: ignore
            users[acception]['friends'].append({ #type: ignore
                'id': g.id,
                'dm': (dm_id := generate_token())
            }) #type: ignore
            g.user['friends'].append({
                'id': g.id,
                'dm': dm_id
            })
            dms[dm_id] = {
                
                'members': [acception, g.id],
                'history': []
            }
            return {
                'success': True,
                'message': 'Friend request accepted successfully!',
                'code': 200
            }, 200
        else:
            return {
                'success': False,
                'message': 'The user or the friend request doesn\'t exist.',
                'code': 404
            }, 404
    else:
        return {
            'success': False,
            'message': 'A field value was missing. ("acception")',
            'code': 400
        }, 400

@me_bp.route('/fr/reject')
def rejectfr():
    rejection = request.form.get('rejection', '')
    if rejection != '':
        if rejection in g.user['friend_requests']['incoming'] and rejection in users.keys():
            g.user['friend_requests']['incoming'].remove(rejection)
            users[rejection]['friend_requests']['outgoing'].remove(g.id) #type: ignore
            if request.form.get('alsoblock', False) == True:
                g.user['blocked'].append(rejection)
            return {
                'success': True
            }, 200
        else:
            return {
                'success': False,
                'message': 'The user or the friend request doesn\'t exist.',
                'code': 404
            }, 404
    else:
        return {
            'success': False,
            'message': 'A field value was missing. ("rejection")',
            'code': 400
        }, 400

@me_bp.route('/fr/cancel')
def cancelfr():
    cancelation = request.form.get('cancelation', '')
    if cancelation != '':
        if cancelation in g.user['friend_requests']['outgoing'] and cancelation in users.keys():
            g.user['friend_requests']['outgoing'].remove(cancelation)
            users[cancelation]['friend_requests']['incoming'].remove(g.id) #type: ignore
            return {
                'success': True
            }, 200
        else:
            return {
                'success': False,
                'message': 'The user or the friend request doesn\'t exist.',
                'code': 404
            }, 404
    else:
        return {
            'success': False,
            'message': 'A field value was missing. ("cancelation")',
            'code': 400
        }, 400