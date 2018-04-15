from flask import Blueprint, current_app, render_template
from flask_login import login_required
from auth.util import Util

# Create and configure app
Application = Blueprint('hr', __name__, template_folder='templates/hr', static_folder='static')

# Util
Util = Util(
    current_app
)


@Application.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('hr/index.html')
