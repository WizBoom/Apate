from flask import Blueprint, current_app, render_template
from flask_login import login_required
from auth.util import Util
from auth.decorators import needs_permission
# Create and configure app
Application = Blueprint('corp_management', __name__, template_folder='templates/corp_management', static_folder='static')

# Util
Util = Util(
    current_app
)


@Application.route('/', methods=['GET', 'POST'])
@login_required
@needs_permission('admin', 'Corp management Landing')
def index():
    return render_template('corp_management/index.html')
