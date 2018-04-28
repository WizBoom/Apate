from flask import Blueprint, render_template

# Create and configure app
Application = Blueprint('esi_parser', __name__, template_folder='templates/esi', static_folder='static')


@Application.route('/')
def index():
    return render_template('esi_parser/index.html')
