from flask import Blueprint, g, render_template as rt, request

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
            'message': f'Updated status to "{request.form["status"]}"'
        }, 200
    else:
        return {
            'code': 400,
            'message': 'A field value was missing. ("status")'
        }, 400