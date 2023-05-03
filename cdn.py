from flask import Blueprint, send_from_directory

cdn = Blueprint('cdn', __name__.split('.')[0], url_prefix='/cdn')

@cdn.route('/__default_user__.webp')
def default_user():
    return send_from_directory('storage/cdn/', '_default_user_.webp')

@cdn.route('/__default_server__.webp')
def default_server():
    return send_from_directory('storage/cdn/', '_default_server_.webp')

@cdn.route('/messages/<_id>/<asset_name>')
def message_cdn(_id, asset_name):
    return send_from_directory('storage/cdn/messages/', f'{_id}/{asset_name}')

@cdn.route('/users/<_id>/<asset_name>')
def user_cdn(_id, asset_name):
    return send_from_directory('storage/cdn/users/', f'{_id}/{asset_name}')

@cdn.route('/servers/<_id>/<asset_name>')
def server_cdn(_id, asset_name):
    return send_from_directory('storage/cdn/servers/', f'{_id}/{asset_name}')