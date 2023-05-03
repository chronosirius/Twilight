from flask import Blueprint, render_template as rt

me_bp = Blueprint('me', __name__.split('.')[0], url_prefix='/me/', template_folder="../templates/locked/me/")

@me_bp.route('/')
def me_main():
    return rt('me.html')