from flask import Blueprint, render_template
from flask_login import login_required

# Create and configure app
Application = Blueprint('hr', __name__, template_folder='templates/hr', static_folder='static')


@Application.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('hr/index.html')
